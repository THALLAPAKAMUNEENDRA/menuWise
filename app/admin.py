from django.contrib import admin
from .models import Supplier, Product

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'country_code', 'active', 'created_at')
    list_filter = ('active', 'country_code')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'supplier', 'supplier_sku', 'price', 'currency', 'unit', 'pack_size', 'imported_at')
    list_filter = ('supplier', 'currency', 'unit')
    search_fields = ('product_name', 'supplier_sku', 'supplier__name')
    list_select_related = ('supplier',)
