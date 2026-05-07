from django.shortcuts import redirect


class BaseTransactionStrategy:
    def execute(self, request, product, form):
        return


class AuthenticatedPurchaseStrategy(BaseTransactionStrategy):
    def execute(self, request, product, form):
        transaction = form.save(commit=False)
        transaction.product = product
        transaction.buyer = request.user.profile
        transaction.status = 'On cart'
        transaction.save()
        return redirect('merchstore:cart')


class GuestPurchaseStrategy(BaseTransactionStrategy):
    def execute(self, request, product, form):
        # Store transaction data in session
        request.session['pending_transaction'] = {
            'product_id': product.pk,
            'amount': form.cleaned_data['amount'],
        }
        return redirect('login')
