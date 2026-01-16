from datetime import date as date_type

from django.db.models import Sum

from apps.bookings.models import Booking
from apps.experiences.models import Experience
from .models import ExperienceAvailability, AvailabilityBlock


def is_date_available(experience: Experience, date: date_type, people: int) -> tuple[bool, str]:
    """
    Valida:
    - experiencia activa
    - people <= max_people
    - si no hay availability configurada => se permite (MVP)
    - si hay availability:
        - enabled
        - dentro de rango (si aplica)
        - weekday permitido (si lista no vacía)
        - no bloqueado
        - no excede capacidad diaria (si aplica)
    """
    if not experience.is_active:
        return False, "Esta experiencia no está activa."

    if people <= 0:
        return False, "El número de personas no es válido."

    if people > experience.max_people:
        return False, f"Máximo permitido por reserva: {experience.max_people} personas."

    try:
        availability = ExperienceAvailability.objects.get(experience=experience)
    except ExperienceAvailability.DoesNotExist:
        # MVP: si no hay reglas, permitimos reservar
        return True, "OK"

    if not availability.is_enabled:
        return False, "Esta experiencia no acepta reservas ahora mismo."

    if availability.start_date and date < availability.start_date:
        return False, "Fecha no disponible (antes del rango permitido)."

    if availability.end_date and date > availability.end_date:
        return False, "Fecha no disponible (después del rango permitido)."

    # weekday(): Lunes=0, Domingo=6
    if availability.weekdays:
        if date.weekday() not in availability.weekdays:
            return False, "Fecha no disponible (día de la semana no permitido)."

    # Bloqueo por fecha (query directa => Pylance OK)
    if AvailabilityBlock.objects.filter(availability=availability, date=date).exists():
        return False, "Fecha bloqueada por el guía."

    # Capacidad diaria total (sumando reservas pending + accepted)
    if availability.daily_capacity_people is not None:
        used_people = (
            Booking.objects.filter(
                experience=experience,
                date=date,
                status__in=[Booking.Status.PENDING, Booking.Status.ACCEPTED],
            ).aggregate(total=Sum("people"))["total"]
        ) or 0

        if used_people + people > availability.daily_capacity_people:
            return False, "No hay capacidad disponible para ese día."

    return True, "OK"
