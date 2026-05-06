from django.db import models
from django.urls import reverse

from accounts.models import Profile


class CommissionType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Commission(models.Model):
    class Status(models.TextChoices):
        OPEN = 'Open'
        FULL = 'Full'

    title = models.CharField(max_length=255)
    description = models.TextField()
    commission_type = models.ForeignKey(
        CommissionType, on_delete=models.SET_NULL, null=True, related_name='commissions'
    )
    maker = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='commissions'
    )
    num_of_people_required = models.PositiveIntegerField()
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.OPEN
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('commissions:detail', args=[self.pk])

    class Meta:
        ordering = ['created_on']


class Job(models.Model):
    class Status(models.TextChoices):
        OPEN = 'Open'
        FULL = 'Full'

    commission = models.ForeignKey(
        Commission, on_delete=models.CASCADE, related_name='jobs'
    )
    role = models.CharField(max_length=255)
    manpower_required = models.PositiveIntegerField()
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.OPEN
    )

    def __str__(self):
        return f'{self.role} ({self.commission.title})'

    class Meta:
        # Open before Full: 'Full' < 'Open' lexically, so reverse status order
        # then manpower DESC, then role ASC
        ordering = ['-status', '-manpower_required', 'role']


class JobApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = 'Pending'
        ACCEPTED = 'Accepted'
        REJECTED = 'Rejected'

    job = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name='applications'
    )
    applicant = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='job_applications'
    )
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.PENDING
    )
    applied_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.applicant} → {self.job.role}'

    class Meta:
        # Pending>Accepted>Rejected can't be expressed with simple field ordering
        # (A<P<R lexically). Service layer applies Case/When annotation for correct order.
        ordering = ['-applied_on']
