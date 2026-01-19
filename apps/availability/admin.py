from django.contrib import admin
from .models import ExperienceAvailability, AvailabilityBlock


class HasDailyPeopleLimitFilter(admin.SimpleListFilter):
    title = "Límite diario (personas)"
    parameter_name = "has_people_limit"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Con límite"),
            ("no", "Sin límite"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(daily_capacity_people__isnull=False)
        if self.value() == "no":
            return queryset.filter(daily_capacity_people__isnull=True)
        return queryset


class HasDailyBookingsLimitFilter(admin.SimpleListFilter):
    title = "Límite diario (excursiones)"
    parameter_name = "has_bookings_limit"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Con límite"),
            ("no", "Sin límite"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(daily_capacity_bookings__isnull=False)
        if self.value() == "no":
            return queryset.filter(daily_capacity_bookings__isnull=True)
        return queryset


@admin.register(ExperienceAvailability)
class ExperienceAvailabilityAdmin(admin.ModelAdmin):
    list_display = (
        "experience",
        "is_enabled",
        "start_date",
        "end_date",
        "daily_capacity_people",
        "daily_capacity_bookings",
        "updated_at",
    )
    list_filter = (
        "is_enabled",
        HasDailyPeopleLimitFilter,
        HasDailyBookingsLimitFilter,
    )
    search_fields = ("experience__title", "experience__guide__username")


@admin.register(AvailabilityBlock)
class AvailabilityBlockAdmin(admin.ModelAdmin):
    list_display = ("availability", "date", "reason")
    list_filter = ("date",)
    search_fields = (
        "availability__experience__title",
        "availability__experience__guide__username",
        "reason",
    )
