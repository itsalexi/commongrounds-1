from django.contrib import admin
from .models import ProjectCategory, Project, Favorite, ProjectReview, ProjectRating


class ProjectCategoryAdmin(admin.ModelAdmin):
    model = ProjectCategory


class ProjectAdmin(admin.ModelAdmin):
    model = Project


# Register your models here.
admin.site.register(ProjectCategory, ProjectCategoryAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register([Favorite, ProjectReview, ProjectRating])
