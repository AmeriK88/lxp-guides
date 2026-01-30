from django.contrib import admin
from .models import HelpCategory, HelpArticle


@admin.register(HelpCategory)
class HelpCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_active")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(HelpArticle)
class HelpArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "is_featured")
    list_filter = ("category", "is_published", "is_featured")
    list_editable = ("is_published", "is_featured")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "content")
