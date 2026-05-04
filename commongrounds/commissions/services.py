from django.db import transaction
from django.db.models import Case, IntegerField, Sum, Value, When

from .models import Commission, Job, JobApplication


class CommissionService:

    @staticmethod
    @transaction.atomic
    def create_commission(author, data, jobs_data):
        commission = Commission.objects.create(maker=author, **data)
        for job_data in jobs_data:
            Job.objects.create(commission=commission, **job_data)
        return commission

    @staticmethod
    def apply_to_job(applicant, job):
        if JobApplication.objects.filter(job=job, applicant=applicant).exists():
            raise ValueError('You have already applied to this job.')
        if job.status == Job.Status.FULL:
            raise ValueError('This job is already full.')
        if job.commission.maker == applicant:
            raise ValueError('You cannot apply to your own commission.')
        return JobApplication.objects.create(job=job, applicant=applicant)

    @staticmethod
    def sync_job_status(job):
        accepted_count = job.applications.filter(
            status=JobApplication.Status.ACCEPTED
        ).count()
        job.status = (
            Job.Status.FULL if accepted_count >= job.manpower_required
            else Job.Status.OPEN
        )
        job.save(update_fields=['status'])

    @staticmethod
    def sync_commission_status(commission):
        jobs = commission.jobs.all()
        if jobs.exists() and all(j.status == Job.Status.FULL for j in jobs):
            commission.status = Commission.Status.FULL
        else:
            commission.status = Commission.Status.OPEN
        commission.save(update_fields=['status'])

    @staticmethod
    def get_commission_summary(commission):
        total = commission.jobs.aggregate(
            s=Sum('manpower_required')
        )['s'] or 0
        accepted = JobApplication.objects.filter(
            job__commission=commission,
            status=JobApplication.Status.ACCEPTED,
        ).count()
        return {
            'total_manpower': total,
            'open_manpower': total - accepted,
        }

    @staticmethod
    def get_ordered_applications(job):
        return job.applications.annotate(
            status_order=Case(
                When(status=JobApplication.Status.PENDING, then=Value(0)),
                When(status=JobApplication.Status.ACCEPTED, then=Value(1)),
                When(status=JobApplication.Status.REJECTED, then=Value(2)),
                default=Value(3),
                output_field=IntegerField(),
            )
        ).order_by('status_order', '-applied_on')
