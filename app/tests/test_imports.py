import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
import io
from app.services.csv_import import process_csv_import
from app.models import Product, Supplier

@pytest.mark.django_db
class TestImports:
    def test_csv_import_valid_and_invalid(self):
        csv_content = """supplier_name,country_code,supplier_sku,product_name,pack_size,unit,currency,price
India Fresh,IN,CHA-001,Chicken Breast,1,kg,,250
Fresh Foods,US,MLK-001,Whole Milk,2,l,USD,4.5
Broken Supplier,US,ERR-001,Invalid Product,-1,kg,USD,-50
"""
        file_obj = io.StringIO(csv_content)
        result = process_csv_import(file_obj)
        
        assert result['success'] is True
        assert result['imported_count'] == 2 # 2 valid rows
        assert len(result['errors']) == 1 # 1 invalid row
        assert "Price cannot be negative" in result['errors'][0]['error'] or "Pack size must be greater than zero" in result['errors'][0]['error']
        
        assert Product.objects.count() == 2
        
        # Check defaults
        india_product = Product.objects.get(supplier_sku='CHA-001')
        assert india_product.currency == 'INR'
        
    def test_csv_import_duplicates(self):
        csv_content = """supplier_name,country_code,supplier_sku,product_name,pack_size,unit,currency,price
Fresh Foods,US,MLK-001,Whole Milk,2,l,USD,4.5
Fresh Foods,US,MLK-001,Whole Milk Duplicate,2,l,USD,5.0
"""
        file_obj = io.StringIO(csv_content)
        result = process_csv_import(file_obj)
        
        assert result['success'] is True
        # Since update_conflicts is True, we only have 1 product
        assert Product.objects.count() == 1
        product = Product.objects.get(supplier_sku='MLK-001')
        assert product.product_name == "Whole Milk Duplicate" # Updated
        assert product.price == 5.0 # Updated
