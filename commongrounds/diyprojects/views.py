from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from accounts.models import Profile
from .forms import ProjectForm, ProjectRatingForm, ProjectReviewForm
from .repositories import ProjectRepository


def project_list(request):
    project_repo = ProjectRepository()
    all_projects = project_repo.get_all()
    created = favorited = reviewed = all_projects.none()

    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        profile = request.user.profile
        created = project_repo.get_created_by(profile)
        favorited = project_repo.get_favorited_by(profile)
        reviewed = project_repo.get_reviewed_by(profile)
        grouped_ids = (
            list(created.values_list('pk', flat=True))
            + list(favorited.values_list('pk', flat=True))
            + list(reviewed.values_list('pk', flat=True))
        )
        all_projects = all_projects.exclude(pk__in=grouped_ids)

    ctx = {
        'projects': all_projects,
        'created_projects': created,
        'favorited_projects': favorited,
        'reviewed_projects': reviewed,
    }

    return render(request, 'project_list.html', ctx)


def project_detail(request, pk):
    project_repo = ProjectRepository()
    project = project_repo.get_by_id(pk)
    review_form = ProjectReviewForm()
    rating_form = ProjectRatingForm()

    if request.method == 'POST' and request.user.is_authenticated:
        profile = request.user.profile
        action = request.POST.get('action')

        if action == 'favorite':
            project_repo.toggle_favorite(project, profile)
            return redirect(project.get_absolute_url())

        if action == 'review':
            review_form = ProjectReviewForm(request.POST, request.FILES)
            if review_form.is_valid():
                project_repo.add_review(project, profile, review_form)
                return redirect(project.get_absolute_url())

        if action == 'rate':
            rating_form = ProjectRatingForm(request.POST)
            if rating_form.is_valid():
                project_repo.add_rating(
                    project, profile, rating_form.cleaned_data['score']
                )
                return redirect(project.get_absolute_url())

    profile = getattr(request.user, 'profile', None)
    is_creator = profile is not None and project.creator_id == profile.id

    ctx = {
        'project': project,
        'review_form': review_form,
        'rating_form': rating_form,
        'reviews': project_repo.get_reviews(project),
        'favorite_count': project_repo.get_favorite_count(project),
        'average_rating': project_repo.get_average_rating(project),
        'is_creator': is_creator,
    }

    return render(request, 'project_detail.html', ctx)


@login_required
def project_create(request):
    profile = getattr(request.user, 'profile', None)
    if profile is None or profile.role != Profile.Role.PROJECT_CREATOR:
        raise PermissionDenied

    project_repo = ProjectRepository()

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = project_repo.create(form, profile)
            return redirect(project.get_absolute_url())
    else:
        form = ProjectForm()

    return render(request, 'project_create.html', {'form': form})


@login_required
def project_update(request, pk):
    project_repo = ProjectRepository()
    project = project_repo.get_by_id(pk)
    profile = getattr(request.user, 'profile', None)

    if profile is None or profile.role != Profile.Role.PROJECT_CREATOR:
        raise PermissionDenied
    if project.creator_id != profile.id:
        raise PermissionDenied

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project_repo.update(form)
            return redirect(project.get_absolute_url())
    else:
        form = ProjectForm(instance=project)

    return render(request, 'project_update.html', {'form': form, 'project': project})
