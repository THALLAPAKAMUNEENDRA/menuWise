import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from app.models import Supplier, Product

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def sample_data():
    supplier1 = Supplier.objects.create(name="Sup 1", country_code="US")
    supplier2 = Supplier.objects.create(name="Sup 2", country_code="IN", active=False)
    
    Product.objects.create(supplier=supplier1, supplier_sku="S1-1", product_name="Milk", pack_size=1, unit="l", currency="USD", price=5)
    Product.objects.create(supplier=supplier1, supplier_sku="S1-2", product_name="Cheese", pack_size=500, unit="g", currency="USD", price=10)
    Product.objects.create(supplier=supplier2, supplier_sku="S2-1", product_name="Paneer", pack_size=1, unit="kg", currency="INR", price=250)
    
    return supplier1, supplier2

@pytest.mark.django_db
class TestAPI:
    def test_get_products(self, api_client, sample_data):
        response = api_client.get('/api/products/')
        assert response.status_code == 200
        assert len(response.data['results']) == 3

    def test_filter_products_by_supplier_active(self, api_client, sample_data):
        response = api_client.get('/api/products/?supplier__active=true')
        assert response.status_code == 200
        assert len(response.data['results']) == 2 # Milk and Cheese are active
        
    def test_search_products_by_name(self, api_client, sample_data):
        response = api_client.get('/api/products/?search=Milk')
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['product_name'] == "Milk"

    def test_filter_products_by_currency(self, api_client, sample_data):
        response = api_client.get('/api/products/?currency=INR')
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['product_name'] == "Paneer"
