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
    
    commission_type = models.ForeignKey(CommissionType, on_delete=models.SET_NULL, null=True, related_name="commissions")
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('commissions:request-details', args=[self.pk])

    class Meta:
        ordering = ['created_on']
