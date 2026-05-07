from django.contrib import admin

from .models import Event, EventSignup, EventType


class EventSignupInline(admin.TabularInline):
    model = EventSignup
    extra = 0


class EventInline(admin.TabularInline):
    model = Event
    extra = 0


class EventTypeAdmin(admin.ModelAdmin):
    inlines = [EventInline]


class EventAdmin(admin.ModelAdmin):
    inlines = [EventSignupInline]
    readonly_fields = ['created_on', 'updated_on']


admin.site.register(EventType, EventTypeAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventSignup)
