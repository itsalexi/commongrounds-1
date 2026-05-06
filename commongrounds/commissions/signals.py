from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import JobApplication
from .services import CommissionService


@receiver(post_save, sender=JobApplication)
def on_application_saved(sender, instance, **kwargs):
    CommissionService.sync_job_status(instance.job)
    CommissionService.sync_commission_status(instance.job.commission)
