from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from accounts.models import Profile
from accounts.mixins import RoleRequiredMixin

from .forms import CommissionForm, JobApplicationForm, JobFormSet
from .models import Commission, Job
from .services import CommissionService


class CommissionListView(ListView):
    model = Commission
    template_name = 'commissions/commission_list.html'
    context_object_name = 'commissions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_commissions = Commission.objects.all()

        if self.request.user.is_authenticated and hasattr(self.request.user, 'profile'):
            profile = self.request.user.profile
            my_commissions = all_commissions.filter(maker=profile)
            applied = all_commissions.filter(
                jobs__applications__applicant=profile
            ).distinct()
            rest = all_commissions.exclude(
                pk__in=my_commissions
            ).exclude(
                pk__in=applied
            )
            context['my_commissions'] = my_commissions
            context['applied_commissions'] = applied
            context['all_commissions'] = rest
        else:
            context['all_commissions'] = all_commissions

        return context


class CommissionDetailView(DetailView):
    model = Commission
    template_name = 'commissions/commission_detail.html'
    context_object_name = 'commission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        commission = self.object
        service = CommissionService()

        jobs = commission.jobs.all()
        jobs_with_data = []
        for job in jobs:
            accepted_count = job.applications.filter(
                status='Accepted'
            ).count()
            jobs_with_data.append({
                'job': job,
                'accepted_count': accepted_count,
                'application_form': JobApplicationForm(),
                'is_full': job.status == Job.Status.FULL,
            })

        context['jobs_with_data'] = jobs_with_data
        context['summary'] = CommissionService.get_commission_summary(commission)
        context['can_edit'] = (
            self.request.user.is_authenticated
            and hasattr(self.request.user, 'profile')
            and self.request.user.profile == commission.maker
        )
        return context


class CommissionCreateView(RoleRequiredMixin, CreateView):
    model = Commission
    form_class = CommissionForm
    template_name = 'commissions/commission_form.html'
    required_role = Profile.Role.COMMISSION_MAKER

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['job_formset'] = JobFormSet(self.request.POST)
        else:
            context['job_formset'] = JobFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        job_formset = context['job_formset']

        if not job_formset.is_valid():
            return self.form_invalid(form)

        jobs_data = [
            f.cleaned_data for f in job_formset
            if f.cleaned_data and not f.cleaned_data.get('DELETE')
        ]

        commission = CommissionService.create_commission(
            author=self.request.user.profile,
            data=form.cleaned_data,
            jobs_data=jobs_data,
        )
        return redirect(commission.get_absolute_url())


class CommissionUpdateView(RoleRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Commission
    form_class = CommissionForm
    template_name = 'commissions/commission_form.html'
    required_role = Profile.Role.COMMISSION_MAKER

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['job_formset'] = JobFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context['job_formset'] = JobFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        job_formset = context['job_formset']

        if not job_formset.is_valid():
            return self.form_invalid(form)

        commission = form.save(commit=False)
        commission.maker = self.object.maker
        commission.save()
        job_formset.instance = commission
        job_formset.save()
        CommissionService.sync_commission_status(commission)
        return redirect(commission.get_absolute_url())


@login_required
def apply_to_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    profile = request.user.profile

    if request.method == 'POST':
        try:
            CommissionService.apply_to_job(applicant=profile, job=job)
            messages.success(request, 'Application submitted successfully.')
        except ValueError as e:
            messages.error(request, str(e))

    return redirect(job.commission.get_absolute_url())
