import pytest
from django.core.exceptions import ValidationError
from app.models import Supplier, Product

@pytest.mark.django_db
class TestModels:
    def test_supplier_creation(self):
        supplier = Supplier.objects.create(name="Test Supplier", country_code="IN")
        assert supplier.name == "Test Supplier"
        assert supplier.active is True

    def test_product_creation_valid(self):
        supplier = Supplier.objects.create(name="Test Supplier", country_code="IN")
        product = Product.objects.create(
            supplier=supplier,
            supplier_sku="SKU-001",
            product_name="Test Product",
            pack_size=1.5,
            unit="kg",
            price=100.0
        )
        assert product.currency == "INR" # Defaults to INR for IN
        assert product.product_name == "Test Product"

    def test_product_price_negative(self):
        supplier = Supplier.objects.create(name="Test Supplier", country_code="US")
        product = Product(
            supplier=supplier,
            supplier_sku="SKU-002",
            product_name="Test Product 2",
            pack_size=1.0,
            unit="kg",
            price=-10.0
        )
        with pytest.raises(ValidationError) as exc:
            product.clean()
        assert 'price' in exc.value.message_dict

    def test_product_invalid_unit(self):
        supplier = Supplier.objects.create(name="Test Supplier", country_code="US")
        product = Product(
            supplier=supplier,
            supplier_sku="SKU-003",
            product_name="Test Product 3",
            pack_size=1.0,
            unit="pounds", # Invalid unit
            price=10.0
        )
        with pytest.raises(ValidationError) as exc:
            product.clean()
        assert 'unit' in exc.value.message_dict

    def test_unique_sku_per_supplier(self):
        from django.db.utils import IntegrityError
        supplier = Supplier.objects.create(name="Test Supplier", country_code="US")
        Product.objects.create(
            supplier=supplier,
            supplier_sku="SKU-004",
            product_name="P1",
            pack_size=1,
            unit="kg",
            price=10
        )
        with pytest.raises(IntegrityError):
            Product.objects.create(
                supplier=supplier,
                supplier_sku="SKU-004", # Duplicate
                product_name="P2",
                pack_size=2,
                unit="kg",
                price=20
            )
