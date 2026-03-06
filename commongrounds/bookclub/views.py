from django.shortcuts import *
from .models import *


def book_list(request):
    books = Book.objects.all()
    genres = Genre.objects.all()
    ctx = {
        'books': books,
        'genres': genres
    }

    return render(request, 'bookclub/book_list.html', ctx)


def book_detail(request, pk):
    book = Book.objects.get(pk=pk)
    ctx = {
        'book': book,
    }
    return render(request, 'bookclub/book_detail.html', ctx)
