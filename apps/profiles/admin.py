from django.contrib import admin
from django.utils import timezone
from .models import GuideProfile, TravelerProfile


@admin.register(GuideProfile)
class GuideProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "verification_status", "verified_at", "verified_by")
    list_filter = ("verification_status",)
    search_fields = ("user__username", "display_name", "languages")

    readonly_fields = ("verified_at", "verified_by")

    fieldsets = (
        ("Datos", {"fields": ("user", "display_name", "bio", "languages", "phone", "instagram", "website")}),
        ("Documentación", {"fields": ("guide_license_document", "insurance_or_registration_document")}),
        ("Verificación", {"fields": ("verification_status", "verification_notes", "verified_at", "verified_by")}),
    )

    def save_model(self, request, obj, form, change):
        # Si pasa a VERIFIED, registramos auditoría
        if "verification_status" in form.changed_data:
            if obj.verification_status == "verified":
                obj.verified_at = timezone.now()
                obj.verified_by = request.user
            elif obj.verification_status in ("pending", "rejected"):
                # Si lo devuelves a pending/rejected, puedes resetear auditoría si quieres:
                obj.verified_at = None
                obj.verified_by = None
        super().save_model(request, obj, form, change)


@admin.register(TravelerProfile)
class TravelerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "created_at")
    search_fields = ("user__username", "display_name")
