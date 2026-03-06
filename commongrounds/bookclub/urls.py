from django.urls import path
from .views import *  # from .views in blogpage, import index function

urlpatterns = [
    path('books', book_list, name='book_list'),
    path('book/<int:pk>', book_detail, name='book_detail'),
]

app_name = 'bookclub'
