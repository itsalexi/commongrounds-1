from django import forms

from .models import Project, ProjectReview


class ProjectReviewForm(forms.ModelForm):
    class Meta:
        model = ProjectReview
        fields = ['comment', 'image']


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'category', 'description', 'materials', 'steps']
        widgets = {
            'category': forms.Select(),
        }
