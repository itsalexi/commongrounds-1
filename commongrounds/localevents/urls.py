from django.urls import path
from .views import event_list, event_detail, event_create, event_update, EventSignupView

urlpatterns = [
    path('events', event_list, name='event_list'),
    path('event/<int:pk>', event_detail, name='event_detail'),
    path('event/add', event_create, name='event_create'),
    path('event/<int:pk>/edit', event_update, name='event_update'),
    path('event/<int:pk>/signup', EventSignupView.as_view(), name='event_signup'),
]

app_name = 'localevents'
