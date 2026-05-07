from django.contrib import admin

from .models import *


class ProductInline(admin.TabularInline):
    model = Product


class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [ProductInline]


class ProductAdmin(admin.ModelAdmin):
    model = Product


class TransactionAdmin(admin.ModelAdmin):
    model = Transaction


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Transaction, TransactionAdmin)
