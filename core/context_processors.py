from apps.bookings.models import Booking


def booking_badges(request):
    if not request.user.is_authenticated:
        return {}

    data = {
        "unseen_traveler_bookings": 0,
        "unseen_guide_bookings": 0,
    }

    # Traveler
    if hasattr(request.user, "is_traveler") and request.user.is_traveler():
        data["unseen_traveler_bookings"] = Booking.objects.filter(
            traveler=request.user,
            seen_by_traveler=False,
        ).count()

    # Guide
    if hasattr(request.user, "is_guide") and request.user.is_guide():
        data["unseen_guide_bookings"] = Booking.objects.filter(
            experience__guide=request.user,
            seen_by_guide=False,
        ).count()

    return data
