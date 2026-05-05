from django.urls import path

from .views import (
    CommissionCreateView,
    CommissionDetailView,
    CommissionListView,
    CommissionUpdateView,
    apply_to_job,
)

app_name = 'commissions'

urlpatterns = [
    path('requests', CommissionListView.as_view(), name='list'),
    path('request/add', CommissionCreateView.as_view(), name='create'),
    path('request/<int:pk>', CommissionDetailView.as_view(), name='detail'),
    path('request/<int:pk>/edit', CommissionUpdateView.as_view(), name='update'),
    path('job/<int:pk>/apply', apply_to_job, name='apply'),
]
