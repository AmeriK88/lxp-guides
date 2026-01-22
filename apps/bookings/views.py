from decimal import Decimal
from urllib import request
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.availability.services import is_date_available
from apps.experiences.models import Experience
from core.decorators import guide_required
from .emails import send_booking_status_email
from .forms import BookingForm, BookingDecisionForm
from .models import Booking
from .forms import BookingChangeRequestForm



@login_required
def create_booking(request, experience_id):
    if not request.user.is_traveler():
        messages.error(request, "Solo los viajeros pueden hacer reservas.")
        return redirect("pages:dashboard")

    experience = get_object_or_404(Experience, pk=experience_id, is_active=True)

    form = BookingForm(request.POST or None, experience=experience)

    if request.method == "POST" and form.is_valid():
        booking = form.save(commit=False)
        booking.experience = experience
        booking.traveler = request.user
        
        # Evitar duplicados: misma experience + misma fecha + mismo traveler en PENDING
        duplicate_exists = Booking.objects.filter(
            traveler=request.user,
            experience=experience,
            date=booking.date,
            status=Booking.Status.PENDING,
        ).exists()

        if duplicate_exists:
            messages.warning(
                request,
                "Ya tienes una solicitud pendiente para esta experiencia en esa fecha. Revisa 'Mis reservas'."
            )
            return redirect("bookings:traveler_list")


        adults = booking.adults or 0
        children = booking.children or 0
        infants = booking.infants or 0

        # Snapshot económico
        unit_price = Decimal(str(experience.price or "0"))
        booking.unit_price = unit_price

        children_unit = unit_price * Decimal("0.5")
        booking.total_price = (unit_price * Decimal(adults)) + (children_unit * Decimal(children))
        # infants gratis

        # Notificaciones no vistas
        booking.seen_by_guide = False
        booking.seen_by_traveler = True

        booking.save()

        # Email al viajero
        message = (
            f"¡Tu reserva ha sido CONFIRMADA!\n\n"
            f"Experiencia: {booking.experience.title}\n"
            f"Fecha: {booking.date}\n\n"
            f"Grupo:\n"
            f"- Adultos: {booking.adults}\n"
            f"- Niños: {booking.children}\n"
            f"- Bebés: {booking.infants}\n\n"
            f"Transporte: {booking.get_transport_mode_display()}\n"
            f"{'Zona/Hotel del viajero: ' + booking.pickup_notes + chr(10) if booking.pickup_notes else ''}"
            f"{'Hora confirmada: ' + booking.pickup_time.strftime('%H:%M') + chr(10) if booking.pickup_time else ''}"
            f"{'Punto de encuentro: ' + booking.meeting_point + chr(10) if booking.meeting_point else ''}\n"
            f"Total: {booking.total_price}€\n\n"
            f"Mensaje del guía:\n{booking.guide_response or '-'}\n"
        )

        messages.success(request, "Reserva enviada al guía.")
        return redirect("bookings:traveler_list")


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
        # Marcar como visto por traveler
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
    if booking.status != Booking.Status.PENDING:
        messages.warning(request, "Esta reserva ya fue gestionada y no se puede aceptar.")
        return redirect("bookings:detail", pk=booking.pk)


    if request.method == "POST":
        form = BookingDecisionForm(request.POST, instance=booking)
        form.require_pickup_time = True
        if form.is_valid():
            booking = form.save(commit=False)

            people = booking.people
            ok, msg = is_date_available(
                booking.experience,
                booking.date,
                people,
                exclude_booking_id=booking.id,
            )

            if not ok:
                messages.error(request, msg or "Ya no hay disponibilidad para esa fecha.")
                return redirect("bookings:detail", pk=booking.pk)

            booking.status = Booking.Status.ACCEPTED
            booking.seen_by_traveler = False
            booking.seen_by_guide = True
            if booking.responded_at is None:
                booking.responded_at = timezone.now()

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
    if booking.status != Booking.Status.PENDING:
        messages.warning(request, "Esta reserva ya fue gestionada y no se puede rechazar.")
        return redirect("bookings:detail", pk=booking.pk)


    if request.method == "POST":
        form = BookingDecisionForm(request.POST, instance=booking)
        form.require_guide_response = True
        if form.is_valid():
            booking = form.save(commit=False)
            booking.status = Booking.Status.REJECTED
            booking.seen_by_traveler = False
            booking.seen_by_guide = True
            if booking.responded_at is None:
                booking.responded_at = timezone.now()

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


@login_required
def request_booking_change(request, pk):
    booking = get_object_or_404(Booking, pk=pk, traveler=request.user)

    # No permitir cambios si ya está finalizada
    if booking.status in [Booking.Status.REJECTED, Booking.Status.CANCELED]:
        messages.error(request, "No puedes modificar una reserva rechazada o cancelada.")
        return redirect("bookings:detail", pk=booking.pk)

    # (Opcional pero recomendable) Evitar doble solicitud si ya hay una pendiente
    if booking.status in [Booking.Status.CHANGE_REQUESTED, Booking.Status.CANCEL_REQUESTED]:
        messages.warning(request, "Ya tienes una solicitud pendiente. Espera a que el guía la gestione.")
        return redirect("bookings:detail", pk=booking.pk)

    form = BookingChangeRequestForm(request.POST or None, booking=booking, instance=booking)

    if request.method == "POST" and form.is_valid():
        # Guardar el estado original para restaurarlo después
        booking.extras["pre_change_status"] = booking.status

        clean = form.cleaned_data.copy()

        # Date a ISO para JSONField
        if clean.get("date"):
            clean["date"] = clean["date"].isoformat()  # "YYYY-MM-DD"

        # Añadir label legible del transporte (para mostrar en templates sin "own_vehicle")
        transport_value = clean.get("transport_mode")
        if transport_value:
            clean["transport_mode_label"] = dict(Booking.TransportMode.choices).get(
                transport_value, transport_value
            )

        # Guardar solicitud
        booking.extras["change_request"] = clean
        booking.status = Booking.Status.CHANGE_REQUESTED

        # Notificaciones “no vistas”
        booking.seen_by_guide = False
        booking.seen_by_traveler = True

        booking.save(update_fields=["extras", "status", "seen_by_guide", "seen_by_traveler", "updated_at"])

        messages.success(request, "Solicitud de cambio enviada al guía.")
        return redirect("bookings:traveler_list")

    return render(request, "bookings/request_change.html", {"booking": booking, "form": form})


@guide_required
def decide_change_request(request, pk, decision):
    booking = get_object_or_404(Booking, pk=pk, experience__guide=request.user)

    if booking.status != Booking.Status.CHANGE_REQUESTED:
        messages.warning(request, "No hay solicitud de cambio pendiente.")
        return redirect("bookings:detail", pk=booking.pk)

    change = (booking.extras or {}).get("change_request")
    if not change:
        messages.error(request, "Solicitud de cambio inválida.")
        return redirect("bookings:detail", pk=booking.pk)

    # Estado anterior (para volver a él tras decidir)
    prev_status = (booking.extras or {}).get("pre_change_status") or Booking.Status.PENDING

    # --- RECHAZAR ---
    if decision == "reject":
        booking.extras.pop("change_request", None)
        booking.extras.pop("pre_change_status", None)

        booking.extras["last_update"] = {
            "type": "change",
            "decision": "rejected",
            "at": timezone.now().isoformat(),
        }

        booking.status = prev_status
        booking.responded_at = timezone.now()
        booking.seen_by_traveler = False
        booking.seen_by_guide = True
        booking.save()

        messages.success(request, "Cambio rechazado.")
        return redirect("bookings:guide_list")

    # --- ACEPTAR ---
    # Aplicar cambios (date viene en ISO)
    if change.get("date"):
        booking.date = date.fromisoformat(change["date"])

    booking.adults = change.get("adults", booking.adults)
    booking.children = change.get("children", booking.children)
    booking.infants = change.get("infants", booking.infants)
    booking.transport_mode = change.get("transport_mode", booking.transport_mode)
    booking.pickup_notes = change.get("pickup_notes", booking.pickup_notes)
    booking.preferred_language = change.get("preferred_language", booking.preferred_language)
    booking.notes = change.get("notes", booking.notes)

    # Recalcular precios (adulto completo, niño 50%, bebé gratis)
    unit_price = Decimal(str(booking.experience.price or "0"))
    booking.unit_price = unit_price
    children_unit = unit_price * Decimal("0.5")
    booking.total_price = (unit_price * Decimal(booking.adults or 0)) + (children_unit * Decimal(booking.children or 0))

    # Validar disponibilidad final (por seguridad)
    ok, msg = is_date_available(
        booking.experience,
        booking.date,
        booking.people,          # people se recalcula en save() por tu modelo
        exclude_booking_id=booking.pk,
    )
    if not ok:
        messages.error(request, msg or "Ya no hay disponibilidad para esa fecha.")
        return redirect("bookings:detail", pk=booking.pk)

    # Limpiar solicitud y registrar actualización
    booking.extras.pop("change_request", None)
    booking.extras.pop("pre_change_status", None)

    booking.extras["last_update"] = {
        "type": "change",
        "decision": "accepted",
        "at": timezone.now().isoformat(),
    }

    # Volver al estado anterior (pending sigue pending / accepted sigue accepted)
    booking.status = prev_status
    booking.responded_at = timezone.now()
    booking.seen_by_traveler = False
    booking.seen_by_guide = True
    booking.save()

    messages.success(request, "Cambio aceptado y aplicado.")
    return redirect("bookings:guide_list")

from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@guide_required
def decide_cancel_request(request, pk, decision):
    booking = get_object_or_404(Booking, pk=pk, experience__guide=request.user)

    if booking.status != Booking.Status.CANCEL_REQUESTED:
        messages.warning(request, "No hay solicitud de cancelación pendiente.")
        return redirect("bookings:detail", pk=booking.pk)

    # Guardamos "la foto" del estado anterior por si quieres volver a él
    pre_status = (booking.extras or {}).get("pre_cancel_status") or Booking.Status.ACCEPTED

    if decision == "reject":
        # limpiar request
        booking.extras.pop("cancel_request", None)

        # volver a estado anterior (más correcto que forzar ACCEPTED siempre)
        booking.status = pre_status

        booking.responded_at = timezone.now()
        booking.seen_by_traveler = False
        booking.seen_by_guide = True

        # banner para el viajero
        booking.extras["last_update"] = {
            "type": "cancel",
            "decision": "rejected",
            "at": timezone.now().isoformat(),
        }

        booking.save(update_fields=[
            "extras", "status", "responded_at",
            "seen_by_traveler", "seen_by_guide", "updated_at"
        ])

        # (Opcional) email si rechaza la cancelación
        # send_booking_status_email(
        #     to_email=booking.traveler.email,
        #     subject="Cancelación rechazada - LanzaXperience",
        #     message=(
        #         f"El guía ha rechazado tu solicitud de cancelación.\n\n"
        #         f"Experiencia: {booking.experience.title}\n"
        #         f"Fecha: {booking.date}\n"
        #     ),
        # )

        messages.success(request, "Cancelación rechazada.")
        return redirect("bookings:guide_list")

    # decision == "accept"
    booking.extras.pop("cancel_request", None)
    booking.status = Booking.Status.CANCELED
    booking.responded_at = timezone.now()
    booking.seen_by_traveler = False
    booking.seen_by_guide = True

    booking.extras["last_update"] = {
        "type": "cancel",
        "decision": "accepted",
        "at": timezone.now().isoformat(),
    }

    booking.save(update_fields=[
        "extras", "status", "responded_at",
        "seen_by_traveler", "seen_by_guide", "updated_at"
    ])

    send_booking_status_email(
        to_email=booking.traveler.email,
        subject="Reserva cancelada - LanzaXperience",
        message=(
            f"Tu reserva para {booking.experience.title} el {booking.date} "
            f"ha sido cancelada por el guía."
        ),
    )

    messages.success(request, "Reserva cancelada correctamente.")
    return redirect("bookings:guide_list")


@login_required
def request_booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, traveler=request.user)

    # No se puede cancelar si ya está cerrada
    if booking.status in [Booking.Status.REJECTED, Booking.Status.CANCELED]:
        messages.error(request, "Esta reserva no se puede cancelar.")
        return redirect("bookings:detail", pk=booking.pk)

    # Evitar duplicados / mezclar flujos
    if booking.status == Booking.Status.CANCEL_REQUESTED:
        messages.info(request, "Ya tienes una solicitud de cancelación pendiente.")
        return redirect("bookings:detail", pk=booking.pk)

    if booking.status == Booking.Status.CHANGE_REQUESTED:
        messages.warning(request, "Tienes una solicitud de cambio pendiente. Espera a que el guía responda antes de cancelar.")
        return redirect("bookings:detail", pk=booking.pk)

    if request.method == "POST":
        reason = (request.POST.get("reason") or "").strip()

        # Guardar estado previo por si el guía rechaza la cancelación
        booking.extras["pre_cancel_status"] = booking.status

        booking.extras["cancel_request"] = {"reason": reason}
        booking.status = Booking.Status.CANCEL_REQUESTED
        booking.seen_by_guide = False
        booking.seen_by_traveler = True

        # (Opcional) Banner/estado de última actualización para el detalle del traveler
        booking.extras["last_update"] = {"type": "cancel", "decision": "requested"}

        booking.save(update_fields=[
            "extras", "status",
            "seen_by_guide", "seen_by_traveler",
            "updated_at"
        ])

        messages.success(request, "Solicitud de cancelación enviada al guía.")
        return redirect("bookings:traveler_list")

    return render(request, "bookings/request_cancel.html", {"booking": booking})
