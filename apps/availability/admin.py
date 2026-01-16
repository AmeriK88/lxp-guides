from django.contrib import admin
from .models import ExperienceAvailability, AvailabilityBlock


@admin.register(ExperienceAvailability)
class ExperienceAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("experience", "is_enabled", "start_date", "end_date", "daily_capacity_people", "updated_at")
    list_filter = ("is_enabled",)
    search_fields = ("experience__title", "experience__guide__username")


@admin.register(AvailabilityBlock)
class AvailabilityBlockAdmin(admin.ModelAdmin):
    list_display = ("availability", "date", "reason")
    list_filter = ("date",)
    search_fields = ("availability__experience__title", "availability__experience__guide__username", "reason")
