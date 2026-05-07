from datetime import timedelta

from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import *
from accounts.models import Profile
from accounts.decorators import role_required
from django.utils import timezone
from .forms import BorrowForm, BookFormFactory


def book_list(request):
    books = Book.objects.all()
    genres = Genre.objects.all()
    ctx = {
        'books': books,
        'genres': genres,
    }

    if request.user.is_authenticated:
        try:
            user_profile = Profile.objects.get(user=request.user)
            contributed_books = Book.objects.filter(contributor=user_profile)
            bookmarked_books = Book.objects.filter(
                bookmarks__profile=user_profile).distinct()
            reviewed_books = Book.objects.filter(
                reviews__user_reviewer=user_profile).distinct()

            ctx.update({
                'contributed_books': contributed_books,
                'bookmarked_books': bookmarked_books,
                'reviewed_books': reviewed_books,
            })
        except Profile.DoesNotExist:
            pass

    return render(request, 'bookclub/book_list.html', ctx)


def book_detail(request, pk):
    book = Book.objects.get(pk=pk)
    reviews = book.reviews.all()
    bookmark_count = book.bookmarks.count()
    is_bookmarked = False
    can_edit_book = False
    user_profile = None

    if request.user.is_authenticated:
        try:
            user_profile = Profile.objects.get(user=request.user)
            is_bookmarked = Bookmark.objects.filter(
                profile=user_profile, book=book).exists()
            can_edit_book = user_profile.role == Profile.Role.BOOK_CONTRIBUTOR
        except Profile.DoesNotExist:
            pass

    if request.method == 'POST':
        form = BookFormFactory.get_form('review', user_profile=user_profile)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            if request.user.is_authenticated and user_profile:
                review.user_reviewer = user_profile
            else:
                review.anon_reviewer = "Anonymous"
            review.save()
            return redirect('bookclub:book_detail', pk=pk)
    else:
        form = BookFormFactory.get_form('review', user_profile=user_profile)

    ctx = {
        'book': book,
        'reviews': reviews,
        'bookmark_count': bookmark_count,
        'is_bookmarked': is_bookmarked,
        'can_edit_book': can_edit_book,
        'form': form,
    }
    return render(request, 'bookclub/book_detail.html', ctx)


@login_required(login_url='/accounts/login/')
def bookmark_toggle(request, pk):
    """Toggle bookmark status for a book."""
    book = Book.objects.get(pk=pk)
    try:
        user_profile = Profile.objects.get(user=request.user)
        bookmark = Bookmark.objects.filter(profile=user_profile, book=book)

        if bookmark.exists():
            bookmark.delete()
        else:
            Bookmark.objects.create(
                profile=user_profile,
                book=book,
                date_bookmarked=timezone.now().date()
            )
    except Profile.DoesNotExist:
        pass

    return redirect('bookclub:book_detail', pk=pk)


def book_borrow(request, pk):
    book = Book.objects.get(pk=pk)

    if not book.available_to_borrow:
        return HttpResponseForbidden('This book is not available to borrow')

    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            pass

    if request.method == 'POST':
        form = BorrowForm(request.POST, profile=user_profile)
        if form.is_valid():
            borrow = form.save(commit=False)
            borrow.book = book
            borrow.date_to_return = borrow.date_borrowed + timedelta(days=14)

            if user_profile:
                borrow.borrower = user_profile
                borrow.name = user_profile.display_name
            else:
                borrow.borrower = None

            borrow.save()
            book.available_to_borrow = False
            book.save(update_fields=['available_to_borrow', 'updated_on'])
            return redirect('bookclub:book_detail', pk=book.pk)
    else:
        initial = {'date_borrowed': timezone.localdate()}
        if user_profile:
            initial['name'] = user_profile.display_name
        form = BorrowForm(initial=initial, profile=user_profile)

    ctx = {
        'book': book,
        'form': form,
        'user_profile': user_profile,
    }
    return render(request, 'bookclub/book_borrow.html', ctx)


@login_required(login_url='/accounts/login/')
def book_add(request):
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return HttpResponseForbidden('Profile not found')

    if user_profile.role != Profile.Role.BOOK_CONTRIBUTOR:
        return HttpResponseForbidden('Unathorized: User is not a Book Contributor')

    if request.method == 'POST':
        form = BookFormFactory.get_form('contribute', user_profile=user_profile)
        if form.is_valid():
            book = form.save(commit=False)
            book.contributor = user_profile
            book.save()
            return redirect('bookclub:book_detail', pk=book.pk)
    else:
        form = BookFormFactory.get_form('contribute', user_profile=user_profile)

    ctx = {
        'form': form,
        'contributor': user_profile,
    }
    return render(request, 'bookclub/book_form.html', ctx)


@role_required(Profile.Role.BOOK_CONTRIBUTOR)
def book_update(request, pk):
    book = Book.objects.get(pk=pk)

    if request.method == 'POST':
        form = BookFormFactory.get_form('update', instance=book)
        if form.is_valid():
            updated_book = form.save(commit=False)
            updated_book.contributor = book.contributor
            updated_book.save()
            return redirect('bookclub:book_detail', pk=updated_book.pk)
    else:
        form = BookFormFactory.get_form('update', instance=book)

    ctx = {
        'form': form,
        'book': book,
    }
    return render(request, 'bookclub/book_update.html', ctx)
