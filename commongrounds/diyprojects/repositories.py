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

    def get_favorites_grouped_by_status(self, profile):
        favorites = (
            Favorite.objects.filter(profile=profile)
            .select_related('project')
        )
        groups = {status.value: [] for status in Favorite.Status}
        for favorite in favorites:
            groups[favorite.project_status].append(favorite)
        return groups

    def get_favorite_for(self, project, profile):
        return Favorite.objects.filter(project=project, profile=profile).first()

    def set_favorite_status(self, project, profile, status):
        if status not in Favorite.Status.values:
            return None
        favorite, _ = Favorite.objects.get_or_create(
            project=project, profile=profile
        )
        favorite.project_status = status
        favorite.save()
        return favorite

    def get_reviews(self, project):
        return ProjectReview.objects.filter(project=project)

    def get_favorite_count(self, project):
        return Favorite.objects.filter(project=project).count()

    def get_average_rating(self, project):
        return ProjectRating.objects.filter(project=project).aggregate(
            avg=Avg('score')
        )['avg']
