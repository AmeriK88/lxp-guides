from django.conf import settings
from django.db import models


class GuideProfile(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="guide_profile",
        limit_choices_to={"role": "guide"},
    )

    display_name = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)
    languages = models.CharField(max_length=200, blank=True)  # ejemplo: "ES, EN, DE"
    phone = models.CharField(max_length=50, blank=True)
    instagram = models.CharField(max_length=120, blank=True)
    website = models.URLField(blank=True)

    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GuideProfile({self.user.username})"


class TravelerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="traveler_profile",
        limit_choices_to={"role": "traveler"},
    )

    display_name = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TravelerProfile({self.user.username})"
