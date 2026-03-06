from django.contrib import admin

from .models import CommissionType, Commission

class CommissionInline(admin.TabularInline):
    model = Commission

class CommissionTypeAdmin(admin.ModelAdmin):
    inlines = [CommissionInline]
    
admin.site.register(Commission)
admin.site.register(CommissionType, CommissionTypeAdmin)
