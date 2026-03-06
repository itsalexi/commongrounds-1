from django.urls import path

from .views import request_details, requests_list

urlpatterns = [
    path('requests', requests_list, name='requests_list'),
    path('request/<int:pk>', request_details, name='request_details'),
]

app_name = 'commissions'
