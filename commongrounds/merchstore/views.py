from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

from .models import Product, Profile, Transaction
from .forms import TransactionForm, ProductForm
from .strategies import AuthenticatedPurchaseStrategy, GuestPurchaseStrategy


class ProductListView(ListView):
    model = Product
    template_name = 'merchstore/product_list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            ctx['user_products'] = Product.objects.filter(
                owner=self.request.user.profile)
            ctx['all_products'] = Product.objects.exclude(
                owner=self.request.user.profile)

        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = 'merchstore/product_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        self.object = self.get_object()

        ctx['can_edit'] = (
            self.request.user.is_authenticated
            and self.request.user == self.object.owner
        )
        ctx['transaction_form'] = TransactionForm()

        return ctx

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        form = TransactionForm(request.POST)

        if form.is_valid():
            if request.user.is_authenticated:
                strategy = AuthenticatedPurchaseStrategy()
            else:
                strategy = GuestPurchaseStrategy()

            return strategy.execute(request, product, form)

        return self.render_to_response(self.get_context_data(transaction_form=form))


class ProductCreateView(CreateView):
    model = Product
    template_name = 'merchstore/product_form.html'
    form_class = ProductForm
    required_role = Profile.Role.MARKET_SELLER

    def form_valid(self, form):
        form.instance.owner = self.request.user.profile
        return super().form_valid(form)


class ProductUpdateView(UpdateView):
    model = Product
    template_name = 'merchstore/product_form.html'
    form_class = ProductForm
    required_role = Profile.Role.MARKET_SELLER

    def form_valid(self, form):
        if form.instance.stock == 0:
            form.instance.status = 'Out of stock'
        return super().form_valid(form)


class CartView(ListView):
    model = Transaction
    template_name = 'merchstore/cart.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['buy_transactions'] = Transaction.objects.filter(
            buyer=self.request.user.profile).order_by('prouct__owner')

        return ctx


class TransactionListview(ListView):
    model = Transaction
    template_name = 'merchstore/transaction_list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['sell_transactions'] = Transaction.objects.filter(
            product__owner=profile).order_by('buyer')

        return ctx
