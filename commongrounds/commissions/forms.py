from django import forms
from django.forms import inlineformset_factory

from .models import Commission, Job, JobApplication


class CommissionForm(forms.ModelForm):
    class Meta:
        model = Commission
        fields = ['title', 'description', 'commission_type', 'num_of_people_required', 'status']
        widgets = {
            'status': forms.Select(),
            'commission_type': forms.Select(),
        }


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['role', 'manpower_required', 'status']
        widgets = {
            'status': forms.Select(),
        }


JobFormSet = inlineformset_factory(
    Commission,
    Job,
    form=JobForm,
    extra=2,
    can_delete=True,
)


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = []
