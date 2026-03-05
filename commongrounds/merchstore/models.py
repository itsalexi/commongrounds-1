from django.db import models


class ProductType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.SET_NULL,
        null=True,
        related_name='product'
    )
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=65)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
