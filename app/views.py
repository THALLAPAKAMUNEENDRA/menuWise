from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from .models import Supplier, Product
from .serializers import SupplierSerializer, ProductSerializer
from .services.csv_import import process_csv_import

class ProductFilter(django_filters.FilterSet):
    supplier__active = django_filters.BooleanFilter(field_name='supplier__active')
    
    class Meta:
        model = Product
        fields = ['supplier', 'currency', 'supplier__active']

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.select_related('supplier').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['product_name']

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser], url_path='import')
    def import_csv(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not file_obj.name.endswith('.csv'):
            return Response({"error": "File is not a CSV"}, status=status.HTTP_400_BAD_REQUEST)

        result = process_csv_import(file_obj)
        
        if not result.get("success"):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)

class SupplierViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
