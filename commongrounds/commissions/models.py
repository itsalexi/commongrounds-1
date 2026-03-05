from django.db import models
from django.urls import reverse

class CommissionType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
     

class Commission(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    num_of_people_required = models.PositiveIntegerField() # Whole numbers are positive integers and 0
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['created_on']