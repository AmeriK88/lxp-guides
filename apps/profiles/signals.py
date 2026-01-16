from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User
from .models import GuideProfile, TravelerProfile


@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance: User, created: bool, **kwargs):
    if not created:
        return

    if instance.role == User.Role.GUIDE:
        GuideProfile.objects.create(user=instance, display_name=instance.username)
    elif instance.role == User.Role.TRAVELER:
        TravelerProfile.objects.create(user=instance, display_name=instance.username)
