from django.urls import path

from accounts.decorators import role_required

from .views import ProductCreateView, ProductDetailView, ProductListView, ProductUpdateView, CartView, TransactionListView

urlpatterns = [
    path('items/', ProductListView.as_view(), name='product_list'),
    path(
        'item/add',
        role_required('Market Seller')(ProductCreateView.as_view()),
        name='product_create',
    ),
    path('item/<int:pk>', ProductDetailView.as_view(), name='product_detail'),
    path('item/<int:pk>/edit', ProductUpdateView.as_view(), name='product_update'),
    path('cart', CartView.as_view, name='cart'),
    path('transactions', TransactionListView.as_view(), name='transaction_list')
]

app_name = 'merchstore'
