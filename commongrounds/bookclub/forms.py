from django import forms
from .models import BookReview, Book, Borrow


class BookReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = ['title', 'comment']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full rounded border border-border bg-white px-3 py-2 text-sm text-text placeholder-text-subtle focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary',
                'placeholder': 'Review title'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'w-full rounded border border-border bg-white px-3 py-2 text-sm text-text placeholder-text-subtle focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary',
                'placeholder': 'Write your review...',
                'rows': 5
            })
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'synopsis',
                  'publication_year', 'available_to_borrow', 'genre']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full rounded border border-border bg-white px-3 py-2 text-sm text-text placeholder-text-subtle focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary',
                'placeholder': 'Book title'
            }),
            'author': forms.TextInput(attrs={
                'class': 'w-full rounded border border-border bg-white px-3 py-2 text-sm text-text placeholder-text-subtle focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary',
                'placeholder': 'Author name'
            }),
            'synopsis': forms.Textarea(attrs={
                'class': 'w-full rounded border border-border bg-white px-3 py-2 text-sm text-text placeholder-text-subtle focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary',
                'placeholder': 'Short synopsis',
                'rows': 6
            }),
            'publication_year': forms.NumberInput(attrs={
                'class': 'w-32 rounded border border-border bg-white px-3 py-2 text-sm text-text focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary',
                'placeholder': '2023'
            }),
            'available_to_borrow': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-primary focus:ring-primary border-border'
            }),
            'genre': forms.Select(attrs={
                'class': 'w-full rounded border border-border bg-white px-3 py-2 text-sm text-text focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary'
            }),
        }


class BorrowForm(forms.ModelForm):
    class Meta:
        model = Borrow
        fields = ['name', 'date_borrowed']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded border border-border bg-white px-3 py-2 text-sm text-text placeholder-text-subtle focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary',
                'placeholder': 'Your name',
            }),
            'date_borrowed': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full rounded border border-border bg-white px-3 py-2 text-sm text-text focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary',
            }),
        }

    def __init__(self, *args, profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = profile

        if profile is not None:
            self.fields['name'].required = False
            self.fields['name'].initial = profile.display_name
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['name'].widget.attrs['value'] = profile.display_name
        else:
            self.fields['name'].required = True
