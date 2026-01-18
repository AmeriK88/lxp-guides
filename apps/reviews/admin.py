from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("experience", "traveler", "rating", "is_public", "created_at")
    list_filter = ("rating", "is_public", "created_at")
    search_fields = ("experience__title", "traveler__username", "traveler__email")
