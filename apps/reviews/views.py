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

    if not traveler_can_review(traveler=request.user, experience=experience):
        messages.error(request, "Solo puedes reseñar si tienes una reserva aceptada en esta experiencia.")
        return redirect("experiences:detail", experience.pk)

    # ✅ Si existe, la editamos. Si no existe, NO la creamos aún.
    review = Review.objects.filter(experience=experience, traveler=request.user).first()

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.experience = experience
            obj.traveler = request.user
            obj.save()

            messages.success(request, "Reseña guardada. ¡Gracias!")
            return redirect("experiences:detail", experience.pk)
    else:
        form = ReviewForm(instance=review)

    stats = Review.objects.filter(experience=experience, is_public=True).aggregate(
        avg=Avg("rating"),
        count=Count("id"),
    )

    return render(
        request,
        "reviews/create.html",
        {"experience": experience, "form": form, "stats": stats, "review": review},
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
    )

    return render(request, "reviews/my_reviews.html", {"reviews": reviews})