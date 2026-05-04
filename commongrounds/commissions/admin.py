from django.contrib import admin

from .models import Commission, CommissionType, Job, JobApplication


class JobApplicationInline(admin.TabularInline):
    model = JobApplication
    extra = 0
    readonly_fields = ['applied_on']


class JobInline(admin.TabularInline):
    model = Job
    extra = 1


@admin.register(CommissionType)
class CommissionTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'maker', 'commission_type', 'status', 'created_on']
    list_filter = ['status', 'commission_type']
    search_fields = ['title', 'maker__display_name']
    inlines = [JobInline]


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['role', 'commission', 'manpower_required', 'status']
    list_filter = ['status']
    inlines = [JobApplicationInline]


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'status', 'applied_on']
    list_filter = ['status']
    readonly_fields = ['applied_on']
