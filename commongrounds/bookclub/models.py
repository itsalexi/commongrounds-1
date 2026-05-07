from django.db import models
from django.urls import *

from accounts.models import Profile


class Genre(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    synopsis = models.TextField(default="")
    publication_year = models.IntegerField()
    available_to_borrow = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    genre = models.ForeignKey(
        Genre, on_delete=models.SET_NULL, null=True
    )
    contributor = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contributed_books',
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('bookclub:book_detail', args=[str(self.pk)])

    class Meta:
        ordering = ['-publication_year']


class BookReview(models.Model):
    user_reviewer = models.ForeignKey(
        Profile, on_delete=models.CASCADE, null=True, blank=True, related_name='book_reviews',
    )
    anon_reviewer = models.TextField(blank=True)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name='reviews',
    )
    title = models.CharField(max_length=255)
    comment = models.TextField()

    def __str__(self):
        return self.title


class Bookmark(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='bookmarks',
    )
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name='bookmarks',
    )
    date_bookmarked = models.DateField()

    def __str__(self):
        return f'{self.profile} bookmarked {self.book}'


class Borrow(models.Model):
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name='borrows',
    )
    borrower = models.ForeignKey(
        Profile, on_delete=models.CASCADE, null=True, blank=True, related_name='borrows',
    )
    name = models.CharField(max_length=255, blank=True)
    date_borrowed = models.DateField()
    date_to_return = models.DateField()

    def __str__(self):
        borrower_name = self.borrower if self.borrower else self.name
        return f'{borrower_name} borrowed {self.book}'
