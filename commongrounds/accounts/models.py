from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Profile(models.Model):
    MARKET_SELLER = 'Market Seller'
    EVENT_ORGANIZER = 'Event Organizer'
    BOOK_CONTRIBUTOR = 'Book Contributor'
    PROJECT_CREATOR = 'Project Creator'
    COMMISSION_MAKER = 'Commission Maker'

    ROLE_CHOICES = [
        (MARKET_SELLER, 'Market Seller'),
        (EVENT_ORGANIZER, 'Event Organizer'),
        (BOOK_CONTRIBUTOR, 'Book Contributor'),
        (PROJECT_CREATOR, 'Project Creator'),
        (COMMISSION_MAKER, 'Commission Maker'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=63)
    email = models.EmailField()
    role = models.CharField(max_length=63, choices=ROLE_CHOICES, blank=True, default='')

    class Meta:
        ordering = ['display_name']

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('accounts:profile_update', args=[self.user.username])
