from django import forms

from .models import Event, EventSignup


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title',
            'category',
            'event_image',
            'description',
            'location',
            'start_time',
            'end_time',
            'event_capacity',
            'status',
        ]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class EventSignupForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        label='Your Name',
        widget=forms.TextInput(attrs={'placeholder': 'Your name'}),
    )
