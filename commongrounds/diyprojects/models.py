from django.db import models
from django.urls import *


class ProjectCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    materials = models.TextField()
    steps = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        ProjectCategory, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_on']

    def get_absolute_url(self):
        return reverse('diyprojects:project_detail', args=[self.pk])
# Create your models here.
