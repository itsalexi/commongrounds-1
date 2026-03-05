from django.urls import path
from .views import project_list, project_detail

app_name = 'diyprojects'

urlpatterns = [
    path('projects/', project_list, name='project_list'),
    path('project/<int:pk>/', project_detail, name='project_detail'),
]
