from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("experience","traveler","rating","status","flagged_reason","created_at","has_guide_reply")
    list_filter = ("rating", "status", "created_at")
    search_fields = ("experience__title", "traveler__username", "traveler__email")
    readonly_fields = ("created_at", "updated_at", "guide_replied_at")

    def has_guide_reply(self, obj):
        return bool(obj.guide_reply and obj.guide_reply.strip())
    has_guide_reply.boolean = True
    has_guide_reply.short_description = "Guide reply"
