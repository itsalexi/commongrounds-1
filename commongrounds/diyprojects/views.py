from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from accounts.models import Profile
from .forms import ProjectForm, ProjectReviewForm
from .models import Favorite, Project, ProjectReview


def project_list(request):
    all_projects = Project.objects.all()
    created = favorited = Project.objects.none()

    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        profile = request.user.profile
        created = all_projects.filter(creator=profile)
        favorited = all_projects.filter(favorite__profile=profile).distinct()

    ctx = {
        'projects': all_projects,
        'created_projects': created,
        'favorited_projects': favorited,
    }

    return render(request, 'project_list.html', ctx)


def project_detail(request, pk):
    project = Project.objects.get(pk=pk)
    review_form = ProjectReviewForm()

    if request.method == 'POST' and request.user.is_authenticated:
        profile = request.user.profile
        action = request.POST.get('action')

        if action == 'favorite':
            Favorite.objects.get_or_create(project=project, profile=profile)
            return redirect(project.get_absolute_url())

        if action == 'review':
            review_form = ProjectReviewForm(request.POST, request.FILES)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.project = project
                review.reviewer = profile
                review.save()
                return redirect(project.get_absolute_url())

    ctx = {
        'project': project,
        'review_form': review_form,
        'reviews': project.projectreview_set.all(),
    }

    return render(request, 'project_detail.html', ctx)


@login_required
def project_create(request):
    profile = getattr(request.user, 'profile', None)
    if profile is None or profile.role != Profile.Role.PROJECT_CREATOR:
        raise PermissionDenied

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.creator = profile
            project.save()
            return redirect(project.get_absolute_url())
    else:
        form = ProjectForm()

    return render(request, 'project_create.html', {'form': form})


@login_required
def project_update(request, pk):
    project = Project.objects.get(pk=pk)
    profile = getattr(request.user, 'profile', None)

    if profile is None or project.creator_id != profile.id:
        raise PermissionDenied

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(project.get_absolute_url())
    else:
        form = ProjectForm(instance=project)

    return render(request, 'project_update.html', {'form': form, 'project': project})
