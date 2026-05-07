from django.db import models
from django.urls import reverse
from accounts.models import Profile
from django.core.validators import MinValueValidator


class ProductType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'Available',
        ON_SALE = 'On sale',
        OUT_OF_STOCK = 'Out of stock'
    name = models.CharField(max_length=255)
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )
    owner = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        null=True,
        related_name='products'
    )
    product_image = models.ImageField(
        upload_to='products/', null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=65)
    stock = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('merchstore:product_detail', args=[self.pk])


class Transaction(models.Model):
    class Status(models.TextChoices):
        ON_CART = 'On cart',
        TO_PAY = 'To pay',
        TO_SHIP = 'To ship',
        TO_RECEIVE = 'To receive',
        DELIVERED = 'Delivered'
    buyer = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transactions'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        related_name='transactions'
    )
    amount = models.IntegerField(validators=[MinValueValidator(1)], default=1)
    status = models.CharField(
        max_length=10,
        choices=Status.choices
    )
    created_on = models.DateTimeField(auto_now_add=True)
