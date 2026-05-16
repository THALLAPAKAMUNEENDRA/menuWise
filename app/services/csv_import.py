import pandas as pd
from typing import Dict, Any, Tuple
from app.models import Supplier, Product
import math
from django.core.exceptions import ValidationError

def process_csv_import(file_obj) -> Dict[str, Any]:
    try:
        df = pd.read_csv(file_obj)
    except Exception as e:
        return {"success": False, "error": f"Failed to read CSV: {str(e)}"}

    required_columns = {'supplier_name', 'country_code', 'supplier_sku', 'product_name', 'pack_size', 'unit', 'currency', 'price'}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        return {"success": False, "error": f"Missing required columns: {', '.join(missing)}"}

    # Replace NaN with None
    df = df.where(pd.notnull(df), None)

    success_count = 0
    errors = []
    
    # 1. Ensure all suppliers exist
    supplier_names = df['supplier_name'].dropna().unique()
    suppliers_db = {}
    
    # We create suppliers if they don't exist
    for _, row in df.drop_duplicates(subset=['supplier_name']).iterrows():
        name = row['supplier_name']
        country_code = row['country_code']
        if not name or not country_code:
            continue
        supplier, _ = Supplier.objects.get_or_create(
            name=name,
            defaults={'country_code': country_code[:2].upper()}
        )
        suppliers_db[name] = supplier

    valid_products = []
    
    for index, row in df.iterrows():
        try:
            supplier_name = row.get('supplier_name')
            if not supplier_name or supplier_name not in suppliers_db:
                raise ValueError("Valid supplier_name is required")
                
            supplier = suppliers_db[supplier_name]
            
            # Extract and validate fields
            price = row.get('price')
            if price is None:
                raise ValueError("Price is missing")
            price = float(price)
            if price < 0:
                raise ValueError("Price cannot be negative")
                
            pack_size = row.get('pack_size')
            if pack_size is None:
                raise ValueError("Pack size is missing")
            pack_size = float(pack_size)
            if pack_size <= 0:
                raise ValueError("Pack size must be greater than zero")
                
            unit = row.get('unit')
            if unit:
                unit = str(unit).lower()
                if unit not in dict(Product.UNIT_CHOICES):
                    raise ValueError(f"Invalid unit: {unit}")
            else:
                raise ValueError("Unit is missing")
                
            currency = row.get('currency')
            # Handle NaN values from pandas (can appear as None, 'nan', float NaN)
            if not currency or str(currency).lower() in ('nan', 'none', ''):
                if supplier.country_code == 'IN':
                    currency = 'INR'
                else:
                    currency = 'USD'
            else:
                currency = str(currency).upper()
                
            supplier_sku = str(row.get('supplier_sku'))
            if not supplier_sku or supplier_sku.lower() == 'none':
                raise ValueError("Supplier SKU is missing")
                
            product_name = str(row.get('product_name'))
            if not product_name or product_name.lower() == 'none':
                raise ValueError("Product name is missing")
                
            product = Product(
                supplier=supplier,
                supplier_sku=supplier_sku,
                product_name=product_name,
                pack_size=pack_size,
                unit=unit,
                currency=currency,
                price=price
            )
            # Run model validation just in case
            product.clean()
            valid_products.append(product)
            
        except ValueError as e:
            errors.append({"row": index + 2, "error": str(e)}) # +2 for 1-based index and header
        except ValidationError as e:
            errors.append({"row": index + 2, "error": str(e.message_dict)})
        except Exception as e:
            errors.append({"row": index + 2, "error": f"Unexpected error: {str(e)}"})

    if valid_products:
        # Use bulk_create with update_conflicts for efficiency and duplicate handling
        try:
            Product.objects.bulk_create(
                valid_products,
                update_conflicts=True,
                unique_fields=['supplier', 'supplier_sku'],
                update_fields=['product_name', 'pack_size', 'unit', 'currency', 'price']
            )
            success_count = len(valid_products)
        except Exception as e:
            return {"success": False, "error": f"Database insertion failed: {str(e)}"}

    return {
        "success": True,
        "imported_count": success_count,
        "errors": errors,
        "total_rows": len(df)
    }
