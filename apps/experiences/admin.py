from django.contrib import admin
from .models import Experience


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("title", "guide", "price", "duration_minutes", "is_active")
    list_filter = ("is_active", "guide")
    search_fields = ("title", "description", "location")
