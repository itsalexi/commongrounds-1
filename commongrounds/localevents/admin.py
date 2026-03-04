from django.contrib import admin
from .models import Event, EventType
# Register your models here.


class EventAdmin(admin.ModelAdmin):
    model = Event


class EventTypeAdmin(admin.ModelAdmin):
    model = EventType


admin.site.register(Event, EventAdmin)
admin.site.register(EventType, EventTypeAdmin)
