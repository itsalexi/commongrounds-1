from django.db import models
from django.urls import reverse

from accounts.models import Profile


class ProjectCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Project(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        ProjectCategory, on_delete=models.SET_NULL, null=True
    )
    creator = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, null=True
    )
    description = models.TextField()
    materials = models.TextField()
    steps = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_on']

    def get_absolute_url(self):
        return reverse('diyprojects:project_detail', args=[self.pk])


class Favorite(models.Model):
    class Status(models.TextChoices):
        BACKLOG = 'Backlog'
        TODO = 'To-Do'
        DONE = 'Done'

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE
    )
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE
    )
    date_favorited = models.DateField(auto_now_add=True)
    project_status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.BACKLOG,
    )


class ProjectReview(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE
    )
    reviewer = models.ForeignKey(
        Profile, on_delete=models.CASCADE
    )
    comment = models.TextField()
    image = models.ImageField(upload_to='reviews/', null=True, blank=True)


class ProjectRating(models.Model):
    SCORE_CHOICES = [(i, str(i)) for i in range(1, 11)]

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE
    )
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE
    )
    score = models.IntegerField(choices=SCORE_CHOICES, default=1)
