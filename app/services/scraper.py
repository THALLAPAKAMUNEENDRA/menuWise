from bs4 import BeautifulSoup
from app.models import Supplier, Product
from django.core.exceptions import ValidationError

def scrape_supplier_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    
    if not table:
        return {"success": False, "error": "No table found in HTML"}

    rows = table.find_all('tr')
    if len(rows) <= 1:
        return {"success": False, "error": "No data rows found"}

    supplier, _ = Supplier.objects.get_or_create(
        name="Scraped Supplier HTML",
        defaults={'country_code': 'US'}
    )

    valid_products = []
    errors = []

    for index, row in enumerate(rows[1:], start=2): # Skip header
        cols = row.find_all('td')
        if len(cols) != 5:
            errors.append({"row": index, "error": "Invalid column count"})
            continue

        item = cols[0].text.strip()
        sku = cols[1].text.strip()
        pack = cols[2].text.strip()
        unit = cols[3].text.strip()
        price = cols[4].text.strip()

        try:
            price_val = float(price)
            pack_val = float(pack)
            unit_val = unit.lower()
            
            product = Product(
                supplier=supplier,
                supplier_sku=sku,
                product_name=item,
                pack_size=pack_val,
                unit=unit_val,
                currency='USD', # Defaulting since not in HTML
                price=price_val
            )
            product.clean()
            valid_products.append(product)
        except (ValueError, ValidationError) as e:
            errors.append({"row": index, "error": str(e)})

    success_count = 0
    if valid_products:
        Product.objects.bulk_create(
            valid_products,
            update_conflicts=True,
            unique_fields=['supplier', 'supplier_sku'],
            update_fields=['product_name', 'pack_size', 'unit', 'currency', 'price']
        )
        success_count = len(valid_products)

    return {
        "success": True,
        "imported_count": success_count,
        "errors": errors
    }
