from django.urls import path
from .views import *  # from .views in blogpage, import index function

urlpatterns = [
    path('books', book_list, name='book_list'),
    path('book/add', book_add, name='book_add'),
    path('book/<int:pk>', book_detail, name='book_detail'),
    path('book/<int:pk>/borrow', book_borrow, name='book_borrow'),
    path('book/<int:pk>/edit', book_update, name='book_update'),
    path('book/<int:pk>/bookmark', bookmark_toggle, name='bookmark_toggle'),
]

app_name = 'bookclub'
