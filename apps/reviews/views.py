from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Exists, OuterRef
from django.shortcuts import get_object_or_404, redirect, render

from apps.experiences.models import Experience
from .forms import ReviewForm
from .models import Review
from .services import traveler_can_review
from django.shortcuts import render
from apps.bookings.models import Booking


@login_required
def create_review(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id, is_active=True)

    # Solo si tiene una reserva aceptada
    if not traveler_can_review(traveler=request.user, experience=experience):
        messages.error(request, "Solo puedes reseñar si tienes una reserva aceptada en esta experiencia.")
        return redirect("experiences:detail", experience.pk)

    # No permitir edición: si ya existe reseña, fuera
    existing = Review.objects.filter(experience=experience, traveler=request.user).first()
    if existing:
        messages.info(request, "Ya has dejado una reseña para esta experiencia. No se puede editar.")
        return redirect("reviews:my_reviews")

    # Booking aceptada para contexto
    booking = (
        Booking.objects.filter(
            traveler=request.user,
            experience=experience,
            status=Booking.Status.ACCEPTED,
        )
        .order_by("-date", "-created_at")
        .first()
    )

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.experience = experience
            obj.traveler = request.user
            obj.booking = booking

            # Moderación: por defecto PENDING (tu modelo ya lo deja así)
            obj.status = Review.Status.PENDING

            obj.save()
            messages.success(request, "Reseña enviada 🙌 (se publicará tras revisión).")
            return redirect("experiences:detail", experience.pk)
    else:
        form = ReviewForm()

    # Stats: SOLO publicadas (lo que ve el público)
    stats = (
        Review.objects.filter(experience=experience, status=Review.Status.PUBLISHED)
        .aggregate(avg=Avg("rating"), count=Count("id"))
    )

    return render(
        request,
        "reviews/create.html",
        {"experience": experience, "form": form, "stats": stats, "review": None},
    )

@login_required
def my_reviews(request):
    accepted_booking_exists = Booking.objects.filter(
        traveler=request.user,
        experience=OuterRef("experience"),
        status=Booking.Status.ACCEPTED,
    )

    reviews = (
        Review.objects.filter(traveler=request.user)
        .select_related("experience", "traveler", "traveler__traveler_profile")
        .annotate(traveler_verified=Exists(accepted_booking_exists))
        .order_by("-created_at")
    )

    return render(request, "reviews/my_reviews.html", {"reviews": reviews})

@login_required
def guide_reviews(request):
    if not request.user.is_guide():
        return redirect("pages:dashboard")

    status = request.GET.get("status")  # pending / published / flagged / None

    qs = Review.objects.filter(experience__guide=request.user).select_related("experience", "traveler")

    if status in [Review.Status.PENDING, Review.Status.PUBLISHED, Review.Status.FLAGGED]:
        qs = qs.filter(status=status)

    reviews = qs.order_by("-created_at")

    return render(request, "reviews/guide_reviews.html", {"reviews": reviews, "status": status})