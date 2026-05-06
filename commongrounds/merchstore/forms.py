from django import forms
from .models import Transaction, Product


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['owner']

        widgets = {
            'product_type': forms.Select(),
            'status': forms.Select(),
        }
