from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, render

from apps.accounts.models import User
from apps.experiences.models import Experience
from apps.reviews.models import Review
from .models import GuideProfile


def public_guide_profile(request, user_id: int):
    guide_user = get_object_or_404(User, pk=user_id, role=User.Role.GUIDE)
    profile = get_object_or_404(GuideProfile, user=guide_user)

    experiences = (
        Experience.objects.filter(guide=guide_user, is_active=True)
        .select_related("guide")
        .order_by("-created_at")
    )

    # Reseñas públicas recibidas (de experiencias de este guía)
    reviews_qs = (
        Review.objects.filter(
            is_public=True,
            experience__guide=guide_user,
        )
        .select_related("experience", "traveler", "traveler__traveler_profile")
        .order_by("-created_at")
    )

    review_stats = reviews_qs.aggregate(
        avg=Avg("rating"),
        count=Count("id"),
    )

    recent_reviews = reviews_qs[:8]  # últimas 8, ajusta si quieres

    return render(
        request,
        "profiles/guide_public.html",
        {
            "guide_user": guide_user,
            "profile": profile,
            "experiences": experiences,
            "recent_reviews": recent_reviews,
            "review_stats": review_stats,
        },
    )
