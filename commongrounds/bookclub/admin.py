from django.contrib import admin
from .models import Book, Genre


class BookAdmin(admin.ModelAdmin):
    model = Book


class GenreAdmin(admin.ModelAdmin):
    model = Genre


admin.site.register(Book, BookAdmin)
admin.site.register(Genre, GenreAdmin)
