from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("experience", "traveler", "date", "people", "status", "created_at", "responded_at")
    list_filter = ("status", "date")
    search_fields = ("experience__title", "traveler__username")
    readonly_fields = ("people", "unit_price", "total_price", "created_at", "updated_at", "responded_at")

