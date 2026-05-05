from django.urls import path
from .views import project_list, project_detail, project_create


urlpatterns = [
    path('projects/', project_list, name='project_list'),
    path('project/create/', project_create, name='project_create'),
    path('project/<int:pk>/', project_detail, name='project_detail'),
]

app_name = 'diyprojects'
