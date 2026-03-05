from django.contrib import admin

from .models import Product, ProductType


class ProductInline(admin.TabularInline):
    model = Product


class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [ProductInline]


class ProductAdmin(admin.ModelAdmin):
    model = Product


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductType, ProductTypeAdmin)
