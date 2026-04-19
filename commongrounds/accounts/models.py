from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=63)
    email = models.EmailField()

    class Meta:
        ordering = ['display_name']

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('accounts:profile_update', args=[self.user.username])
