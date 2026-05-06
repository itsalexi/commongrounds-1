from django.db.models import Avg

from .models import Favorite, Project, ProjectRating, ProjectReview


class ProjectRepository:
    def get_all(self):
        return Project.objects.all()

    def get_by_category(self, category_name):
        return Project.objects.filter(category__name=category_name)

    def get_recent(self, n):
        return Project.objects.order_by('-created_on')[:n]

    def get_by_id(self, id):
        return Project.objects.get(pk=id)

    def get_created_by(self, profile):
        return Project.objects.filter(creator=profile)

    def get_favorited_by(self, profile):
        return Project.objects.filter(favorite__profile=profile).distinct()

    def get_reviewed_by(self, profile):
        return Project.objects.filter(projectreview__reviewer=profile).distinct()

    def get_reviews(self, project):
        return ProjectReview.objects.filter(project=project)

    def get_favorite_count(self, project):
        return Favorite.objects.filter(project=project).count()

    def get_average_rating(self, project):
        return ProjectRating.objects.filter(project=project).aggregate(
            avg=Avg('score')
        )['avg']

    def toggle_favorite(self, project, profile):
        Favorite.objects.get_or_create(project=project, profile=profile)

    def add_review(self, project, profile, form):
        review = form.save(commit=False)
        review.project = project
        review.reviewer = profile
        review.save()
        return review

    def add_rating(self, project, profile, score):
        return ProjectRating.objects.create(
            project=project, profile=profile, score=score
        )

    def create(self, form, profile):
        project = form.save(commit=False)
        project.creator = profile
        project.save()
        return project

    def update(self, form):
        return form.save()
