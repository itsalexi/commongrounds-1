from django.urls import path

from accounts.decorators import role_required

from .views import ProductCreateView, ProductDetailView, ProductListView

urlpatterns = [
    path('items/', ProductListView.as_view(), name='product_list'),
    path(
        'item/add',
        role_required('Market Seller')(ProductCreateView.as_view()),
        name='product_create',
    ),
    path('item/<int:pk>', ProductDetailView.as_view(), name='product_detail')
]

app_name = 'merchstore'
