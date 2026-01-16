from django.shortcuts import get_object_or_404, render

from apps.accounts.models import User
from apps.experiences.models import Experience
from .models import GuideProfile


def public_guide_profile(request, user_id: int):
    guide_user = get_object_or_404(User, pk=user_id, role=User.Role.GUIDE)
    profile = get_object_or_404(GuideProfile, user=guide_user)

    experiences = (
        Experience.objects.filter(guide=guide_user, is_active=True)
        .select_related("guide")
        .order_by("-created_at")
    )

    return render(
        request,
        "profiles/guide_public.html",
        {"guide_user": guide_user, "profile": profile, "experiences": experiences},
    )
