from django.contrib import admin
from .models import Experience, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("title", "guide", "category", "price", "duration_minutes", "is_active")
    list_filter = ("is_active", "category")
    search_fields = ("title", "description", "location", "guide__username")
