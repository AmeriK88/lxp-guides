from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.experiences.models import Experience
from core.decorators import guide_required
from .forms import BookingForm
from .models import Booking
from apps.availability.services import is_date_available


@login_required
def create_booking(request, experience_id):
    if not request.user.is_traveler():
        messages.error(request, "Solo los viajeros pueden hacer reservas.")
        return redirect("pages:dashboard")

    experience = get_object_or_404(Experience, pk=experience_id, is_active=True)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data["date"]
            people = form.cleaned_data["people"]

            ok, msg = is_date_available(experience, date, people)
            if not ok:
                messages.error(request, msg)
                return render(request, "bookings/create.html", {"form": form, "experience": experience})

            booking = form.save(commit=False)
            booking.experience = experience
            booking.traveler = request.user
            booking.save()
            messages.success(request, "Reserva enviada al guía.")
            return redirect("bookings:traveler_list")

    else:
        form = BookingForm()

    return render(request, "bookings/create.html", {"form": form, "experience": experience})


@login_required
def traveler_bookings(request):
    bookings = Booking.objects.filter(traveler=request.user).select_related("experience")
    return render(request, "bookings/traveler_list.html", {"bookings": bookings})


@guide_required
def guide_bookings(request):
    bookings = Booking.objects.filter(
        experience__guide=request.user
    ).select_related("experience", "traveler")
    return render(request, "bookings/guide_list.html", {"bookings": bookings})


@guide_required
def accept_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, experience__guide=request.user)
    booking.status = Booking.Status.ACCEPTED
    booking.save()
    messages.success(request, "Reserva aceptada.")
    return redirect("bookings:guide_list")


@guide_required
def reject_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, experience__guide=request.user)
    booking.status = Booking.Status.REJECTED
    booking.save()
    messages.success(request, "Reserva rechazada.")
    return redirect("bookings:guide_list")
