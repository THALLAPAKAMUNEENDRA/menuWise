from rest_framework import serializers
from .models import Supplier, Product

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'country_code', 'active', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    supplier_details = SupplierSerializer(source='supplier', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'supplier', 'supplier_details', 'supplier_sku', 
            'product_name', 'pack_size', 'unit', 'currency', 'price', 'imported_at'
        ]
