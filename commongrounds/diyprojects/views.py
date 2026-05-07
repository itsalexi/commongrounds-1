from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from accounts.models import Profile
from .forms import ProjectForm, ProjectRatingForm, ProjectReviewForm
from .models import Favorite, ProjectRating
from .repositories import ProjectRepository


def project_list(request):
    project_repo = ProjectRepository()
    all_projects = project_repo.get_all()
    created = reviewed = all_projects.none()
    favorites_by_status = {status.value: [] for status in Favorite.Status}
    can_create_project = False

    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        profile = request.user.profile
        can_create_project = profile.role == Profile.Role.PROJECT_CREATOR
        created = project_repo.get_created_by(profile)
        favorited = project_repo.get_favorited_by(profile)
        reviewed = project_repo.get_reviewed_by(profile)
        favorites_by_status = project_repo.get_favorites_grouped_by_status(profile)
        all_projects = all_projects.exclude(
            pk__in=created.values_list('pk', flat=True)
        ).exclude(
            pk__in=favorited.values_list('pk', flat=True)
        ).exclude(
            pk__in=reviewed.values_list('pk', flat=True)
        )

    favorite_buckets = [
        ('Backlog', favorites_by_status.get(Favorite.Status.BACKLOG.value, [])),
        ('To-Do', favorites_by_status.get(Favorite.Status.TODO.value, [])),
        ('Done', favorites_by_status.get(Favorite.Status.DONE.value, [])),
    ]
    has_favorites = any(bucket for _, bucket in favorite_buckets)

    ctx = {
        'projects': all_projects,
        'created_projects': created,
        'favorite_buckets': favorite_buckets,
        'has_favorites': has_favorites,
        'reviewed_projects': reviewed,
        'can_create_project': can_create_project,
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
            Favorite.objects.get_or_create(project=project, profile=profile)
            return redirect(project.get_absolute_url())

        if action == 'set_status':
            new_status = request.POST.get('project_status', '')
            project_repo.set_favorite_status(project, profile, new_status)
            return redirect(project.get_absolute_url())

        if action == 'review':
            review_form = ProjectReviewForm(request.POST, request.FILES)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.project = project
                review.reviewer = profile
                review.save()
                return redirect(project.get_absolute_url())

        if action == 'rate':
            rating_form = ProjectRatingForm(request.POST)
            if rating_form.is_valid():
                ProjectRating.objects.create(
                    project=project,
                    profile=profile,
                    score=rating_form.cleaned_data['score'],
                )
                return redirect(project.get_absolute_url())

    profile = getattr(request.user, 'profile', None)
    is_creator = profile is not None and project.creator_id == profile.id
    user_favorite = (
        project_repo.get_favorite_for(project, profile) if profile else None
    )

    ctx = {
        'project': project,
        'review_form': review_form,
        'rating_form': rating_form,
        'reviews': project_repo.get_reviews(project),
        'favorite_count': project_repo.get_favorite_count(project),
        'average_rating': project_repo.get_average_rating(project),
        'is_creator': is_creator,
        'user_favorite': user_favorite,
        'status_choices': Favorite.Status.choices,
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
            form.save()
            return redirect(project.get_absolute_url())
    else:
        form = ProjectForm(instance=project)

    return render(request, 'project_update.html', {'form': form, 'project': project})
