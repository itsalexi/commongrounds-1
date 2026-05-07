from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Profile


class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=Profile.Role.choices, label='Register as')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['password2'].label = 'Confirm password'
        self.order_fields(['username', 'role', 'password1', 'password2'])


class ProfileUpdateForm(forms.ModelForm):
    role = forms.ChoiceField(choices=Profile.Role.choices)

    class Meta:
        model = Profile
        fields = ['display_name', 'role']
