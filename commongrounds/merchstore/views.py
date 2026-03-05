from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from .models import Product, ProductType


class ProductListView(ListView):
    model = ProductType
    context_object_name = 'product_types'
    template_name = 'merchstore/product_list.html'


class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'item'
    template_name = 'merchstore/product_detail.html'
