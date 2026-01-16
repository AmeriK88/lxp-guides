from django.contrib import admin
from .models import GuideProfile, TravelerProfile


@admin.register(GuideProfile)
class GuideProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "verification_status", "languages", "phone")
    list_filter = ("verification_status",)
    search_fields = ("user__username", "display_name", "languages")


@admin.register(TravelerProfile)
class TravelerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "created_at")
    search_fields = ("user__username", "display_name")
