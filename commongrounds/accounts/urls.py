from django.urls import path

from .views import profile_update, register

urlpatterns = [
    path('register', register, name='register'),
    path('<str:username>', profile_update, name='profile_update'),
]

app_name = 'accounts'
