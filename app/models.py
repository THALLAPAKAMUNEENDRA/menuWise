from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    country_code = models.CharField(max_length=2)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    UNIT_CHOICES = [
        ('g', 'Grams'),
        ('kg', 'Kilograms'),
        ('ml', 'Milliliters'),
        ('l', 'Liters'),
        ('each', 'Each'),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='products')
    supplier_sku = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    pack_size = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    currency = models.CharField(max_length=3)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    imported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-imported_at', 'id']
        constraints = [
            models.UniqueConstraint(fields=['supplier', 'supplier_sku'], name='unique_supplier_sku')
        ]

    def clean(self):
        super().clean()
        if self.price is not None and self.price < 0:
            raise ValidationError({'price': 'Price cannot be negative.'})
        if self.pack_size is not None and self.pack_size <= 0:
            raise ValidationError({'pack_size': 'Pack size must be greater than zero.'})
        
        # Normalize unit
        if self.unit:
            self.unit = self.unit.lower()
            if self.unit not in dict(self.UNIT_CHOICES):
                raise ValidationError({'unit': 'Invalid unit.'})

        # Currency defaulting
        if not self.currency:
            if self.supplier and self.supplier.country_code == 'IN':
                self.currency = 'INR'
            else:
                self.currency = 'USD'
        else:
            self.currency = self.currency.upper()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} ({self.supplier_sku})"
