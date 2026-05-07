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

    def __init__(self, *args, user_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user_profile:
            self.user_profile = user_profile
            self.fields['title'].widget.attrs['readonly'] = True
            self.fields['comment'].widget.attrs['readonly'] = True
        else:
            self.user_profile = None


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


class BookContributeForm(forms.ModelForm):
    """Form for creating a new book with contributor pre-set."""
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

    def __init__(self, *args, user_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_profile = user_profile


class BookUpdateForm(forms.ModelForm):
    """Form for updating a book, excludes the Contributor field."""
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

    def __init__(self, *args, user_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_profile = user_profile


class BookFormFactory:
    """Factory class for creating appropriate form instances based on context."""

    @classmethod
    def get_form(cls, context, user_profile=None, instance=None):
        """
        Return a form class based on the context.

        Args:
            context (str): One of 'review', 'contribute', or 'update'
            user_profile: The logged-in user's profile (for pre-population)
            instance: The Book instance (for update forms)

        Returns:
            A form class (not instance) configured for the given context
        """
        if context == 'review':
            return cls._create_review_form(user_profile, instance)
        elif context == 'contribute':
            return cls._create_contribute_form(user_profile, instance)
        elif context == 'update':
            return cls._create_update_form(user_profile, instance)
        else:
            raise ValueError(f"Invalid context: {context}")

    @classmethod
    def _create_review_form(cls, user_profile=None, instance=None):
        """Create a BookReviewForm with reviewer pre-set and read-only."""
        return BookReviewForm(instance=instance, user_profile=user_profile)

    @classmethod
    def _create_contribute_form(cls, user_profile=None, instance=None):
        """Create a BookContributeForm with contributor pre-set."""
        return BookContributeForm(instance=instance, user_profile=user_profile)

    @classmethod
    def _create_update_form(cls, user_profile=None, instance=None):
        """Create a BookUpdateForm (excludes contributor field)."""
        return BookUpdateForm(instance=instance, user_profile=user_profile)


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
