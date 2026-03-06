from django.urls import path

from .views import request_details, requests_list

urlpatterns = [
    path("requests", requests_list, name="requests-list"),
    path("request/<int:request_id>", request_details, name="request-details"),
]

app_name = "commissions"
