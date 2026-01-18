from __future__ import annotations
from typing import Protocol
from apps.bookings.models import Booking
from apps.experiences.models import Experience


class TravelerUser(Protocol):
    def is_traveler(self) -> bool: ...


def traveler_can_review(*, traveler: TravelerUser, experience: Experience) -> bool:
    if not traveler.is_traveler():
        return False

    return Booking.objects.filter(
        traveler=traveler,
        experience=experience,
        status=Booking.Status.ACCEPTED,
    ).exists()
