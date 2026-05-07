from django.urls import path

from .views import ask, stream


app_name = 'askagent'

urlpatterns = [
    path('', ask, name='ask'),
    path('stream/', stream, name='stream'),
]
