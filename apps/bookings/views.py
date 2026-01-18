from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.availability.services import is_date_available
from apps.experiences.models import Experience
from core.decorators import guide_required
from .emails import send_booking_status_email
from .forms import BookingForm, BookingDecisionForm
from .models import Booking


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
            adults = form.cleaned_data.get("adults") or 0
            children = form.cleaned_data.get("children") or 0
            infants = form.cleaned_data.get("infants") or 0

            people = adults + children + infants  # total real para disponibilidad/capacidad

            ok, msg = is_date_available(experience, date, people)
            if not ok:
                messages.error(request, msg)
                return render(request, "bookings/create.html", {"form": form, "experience": experience})

            booking = form.save(commit=False)
            booking.experience = experience
            booking.traveler = request.user

            # Si aún mantienes el campo "people" en el modelo (compatibilidad con listados antiguos)
            if hasattr(booking, "people"):
                booking.people = people

            # Snapshot económico
            unit_price = Decimal(str(experience.price or "0"))
            booking.unit_price = unit_price

            children_unit = (unit_price * Decimal("0.5"))  # niños al 50%
            total_price = (unit_price * Decimal(adults)) + (children_unit * Decimal(children))
            # infants = gratis

            booking.total_price = total_price

            # Notificaciones no vistas
            booking.seen_by_guide = False
            booking.seen_by_traveler = True

            booking.save()

            # Email al viajero (confirmación de solicitud)
            send_booking_status_email(
                to_email=request.user.email,
                subject="Solicitud de reserva recibida - LanzaXperience",
                message=(
                    f"Hemos recibido tu solicitud.\n\n"
                    f"Experiencia: {experience.title}\n"
                    f"Fecha: {booking.date}\n"
                    f"Adultos: {adults}\n"
                    f"Niños: {children}\n"
                    f"Bebés: {infants}\n"
                    f"Transporte: {booking.get_transport_mode_display()}\n"
                    f"{'Recogida/Zona: ' + booking.pickup_notes + chr(10) if booking.pickup_notes else ''}"
                    f"Total estimado: {booking.total_price}€\n\n"
                    f"Estado: PENDIENTE (el guía debe aceptarla)\n"
                ),
            )

            messages.success(request, "Reserva enviada al guía.")
            return redirect("bookings:traveler_list")
    else:
        form = BookingForm()

    return render(request, "bookings/create.html", {"form": form, "experience": experience})


@login_required
def traveler_bookings(request):
    bookings = (
        Booking.objects.filter(traveler=request.user)
        .select_related("experience", "experience__guide")
    )
    return render(request, "bookings/traveler_list.html", {"bookings": bookings})


@guide_required
def guide_bookings(request):
    bookings = (
        Booking.objects.filter(experience__guide=request.user)
        .select_related("experience", "traveler")
    )
    return render(request, "bookings/guide_list.html", {"bookings": bookings})


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related("experience", "experience__guide", "traveler"),
        pk=pk,
    )

    # Permisos: traveler dueño o guide dueño de la experience
    if request.user == booking.traveler:
        # ✅ Marcar como visto por traveler
        if not booking.seen_by_traveler:
            booking.seen_by_traveler = True
            booking.save(update_fields=["seen_by_traveler"])

    elif request.user.is_guide() and booking.experience.guide == request.user:
        # (Opcional) marcar como visto por guía si entras al detalle
        if not booking.seen_by_guide:
            booking.seen_by_guide = True
            booking.save(update_fields=["seen_by_guide"])

    else:
        messages.error(request, "No tienes permiso para ver esta reserva.")
        return redirect("pages:dashboard")

    return render(request, "bookings/detail.html", {"booking": booking})


@guide_required
def accept_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, experience__guide=request.user)

    if request.method == "POST":
        form = BookingDecisionForm(request.POST, instance=booking)
        form.require_pickup_time = True
        if form.is_valid():
            booking = form.save(commit=False)
            booking.status = Booking.Status.ACCEPTED
            booking.seen_by_traveler = False
            booking.seen_by_guide = True

            booking.save()

            send_booking_status_email(
                to_email=booking.traveler.email,
                subject="Reserva aceptada - LanzaXperience",
                message=(
                    f"¡Tu reserva ha sido CONFIRMADA!\n\n"
                    f"Experiencia: {booking.experience.title}\n"
                    f"Fecha: {booking.date}\n\n"
                    f"Grupo:\n"
                    f"- Adultos: {booking.adults}\n"
                    f"- Niños: {booking.children}\n"
                    f"- Bebés: {booking.infants}\n\n"
                    f"Transporte: {booking.get_transport_mode_display()}\n"
                    f"Recogida: {booking.pickup_notes or 'Por concretar con el guía'}\n\n"
                    f"Total: {booking.total_price}€\n\n"
                    f"Mensaje del guía:\n{booking.guide_response or '-'}\n"
                ),
            )

            messages.success(request, "Reserva aceptada.")
            return redirect("bookings:guide_list")
    else:
        form = BookingDecisionForm(instance=booking)

    return render(request, "bookings/decision.html", {"booking": booking, "form": form, "action": "accept"})


@guide_required
def reject_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, experience__guide=request.user)

    if request.method == "POST":
        form = BookingDecisionForm(request.POST, instance=booking)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.status = Booking.Status.REJECTED
            booking.seen_by_traveler = False
            booking.seen_by_guide = True
            booking.save()

            send_booking_status_email(
                to_email=booking.traveler.email,
                subject="Reserva rechazada - LanzaXperience",
                message=(
                    f"Tu solicitud de reserva ha sido RECHAZADA.\n\n"
                    f"Experiencia: {booking.experience.title}\n"
                    f"Fecha solicitada: {booking.date}\n\n"
                    f"Grupo:\n"
                    f"- Adultos: {booking.adults}\n"
                    f"- Niños: {booking.children}\n"
                    f"- Bebés: {booking.infants}\n\n"
                    f"Transporte: {booking.get_transport_mode_display()}\n"
                    f"Punto de recogida: {booking.pickup_notes or 'No especificado'}\n\n"
                    f"Precio por adulto: {booking.unit_price}€\n"
                    f"Total estimado: {booking.total_price}€\n\n"
                    f"Mensaje del guía:\n{booking.guide_response or '-'}\n"
                ),
            )

            messages.success(request, "Reserva rechazada.")
            return redirect("bookings:guide_list")
    else:
        form = BookingDecisionForm(instance=booking)

    return render(request, "bookings/decision.html", {
        "booking": booking,
        "form": form,
        "action": "reject",
    })

