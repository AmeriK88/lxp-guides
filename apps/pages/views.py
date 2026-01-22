from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from apps.profiles.forms import GuideProfileForm, TravelerProfileForm
from django.db.models import Count, Q, Sum

from apps.experiences.models import Experience, Category
from apps.bookings.models import Booking
from apps.reviews.models import Review

from decimal import Decimal
from django.utils import timezone
from datetime import timedelta


def home_view(request):
    featured_experiences = (
        Experience.objects
        .filter(is_active=True)
        .select_related("guide", "category")
        .order_by("-created_at")[:6]
    )

    return render(request, "pages/home.html", {
        "featured_experiences": featured_experiences,
    })


@login_required
def dashboard_redirect(request):
    if request.user.is_guide():
        return redirect("pages:guide_dashboard")
    return redirect("pages:traveler_dashboard")


@login_required
def guide_dashboard(request):
    if not request.user.is_guide():
        return redirect("pages:dashboard")

    today = timezone.localdate()
    since = today - timedelta(days=30)

    experiences_qs = Experience.objects.filter(guide=request.user, is_active=True)
    experiences_count = experiences_qs.count()

    guide_bookings_qs = Booking.objects.filter(experience__guide=request.user)

    bookings_30d = guide_bookings_qs.filter(created_at__date__gte=since).count()

    # Pendientes “de acción” para el guía (NUEVO)
    pending_new = guide_bookings_qs.filter(status=Booking.Status.PENDING).count()
    pending_change = guide_bookings_qs.filter(status=Booking.Status.CHANGE_REQUESTED).count()
    pending_cancel = guide_bookings_qs.filter(status=Booking.Status.CANCEL_REQUESTED).count()

    pending_total = pending_new + pending_change + pending_cancel

    revenue_30d = (
        guide_bookings_qs.filter(
            status=Booking.Status.ACCEPTED,
            created_at__date__gte=since,
        )
        .aggregate(total=Sum("total_price"))["total"]
        or Decimal("0.00")
    )

    # “No vistas” por el guía (ya lo tenías)
    unseen_guide_bookings = guide_bookings_qs.filter(seen_by_guide=False).count()

    # Reservas recientes: puedes priorizar las que requieren acción arriba (opcional)
    recent_bookings = (
        guide_bookings_qs.select_related("experience", "traveler")
        .order_by("-created_at")[:8]
    )

    reviews_total = Review.objects.filter(
        experience__guide=request.user,
        status=Review.Status.PUBLISHED,
    ).count()

    kpis = {
        "experiences": experiences_count,
        "bookings_30d": bookings_30d,

        # Aquí cambiamos pending para que sea “pendientes totales”
        "pending": pending_total,

        # Si quieres mostrar desglose en el template
        "pending_new": pending_new,
        "pending_change": pending_change,
        "pending_cancel": pending_cancel,

        "revenue_30d": revenue_30d,
        "reviews": reviews_total,
    }

    return render(
        request,
        "pages/guide_dashboard.html",
        {
            "kpis": kpis,
            "unseen_guide_bookings": unseen_guide_bookings,
            "recent_bookings": recent_bookings,
        },
    )


@login_required
def traveler_dashboard(request):
    # Solo traveler
    if request.user.is_guide():
        return redirect("pages:dashboard")

    today = timezone.localdate()
    since = today - timedelta(days=30)

    categories = Category.objects.all()

    # Top experiencias (por reservas pending+accepted). Si no hay reservas, se ordena por created_at.
    top_experiences = (
        Experience.objects.filter(is_active=True)
        .select_related("guide", "category")
        .annotate(
            bookings_count=Count(
                "bookings",
                filter=Q(bookings__status__in=[Booking.Status.PENDING, Booking.Status.ACCEPTED]),
            )
        )
        .order_by("-bookings_count", "-created_at")[:6]
    )

    # Bookings del traveler
    traveler_bookings_qs = Booking.objects.filter(traveler=request.user).select_related("experience", "experience__guide")

    # KPIs
    bookings_30d = traveler_bookings_qs.filter(created_at__date__gte=since).count()
    accepted = traveler_bookings_qs.filter(status=Booking.Status.ACCEPTED).count()
    rejected = traveler_bookings_qs.filter(status=Booking.Status.REJECTED).count()
    pending = traveler_bookings_qs.filter(status=Booking.Status.PENDING).count()

    spent_30d = (
        traveler_bookings_qs.filter(
            status=Booking.Status.ACCEPTED,
            created_at__date__gte=since,
        ).aggregate(total=Sum("total_price"))["total"]
        or Decimal("0.00")
    )

    unseen_traveler_bookings = traveler_bookings_qs.filter(seen_by_traveler=False).count()

    # Próxima reserva (futura) - yo excluiría canceled y rejected
    next_booking = (
        traveler_bookings_qs.filter(date__gte=today)
        .exclude(status__in=[Booking.Status.REJECTED, Booking.Status.CANCELED])
        .order_by("date", "created_at")
        .first()
    )

    # Tabla reservas recientes
    recent_bookings = traveler_bookings_qs.order_by("-created_at")[:8]

    reviews_count = request.user.reviews.filter(
        status=Review.Status.PUBLISHED
    ).count()

    kpis = {
        "bookings_30d": bookings_30d,
        "spent_30d": spent_30d,
        "accepted": accepted,
        "rejected": rejected,
        "pending": pending,
        "reviews": reviews_count,
    }

    return render(
        request,
        "pages/traveler_dashboard.html",
        {
            "categories": categories,
            "top_experiences": top_experiences,
            "kpis": kpis,
            "unseen_traveler_bookings": unseen_traveler_bookings,
            "next_booking": next_booking,
            "recent_bookings": recent_bookings,
        },
    )

@login_required
def profile_view(request):
    if request.user.is_guide():
        profile = request.user.guide_profile
        FormClass = GuideProfileForm
        template = "profiles/guide_edit.html"
    else:
        profile = request.user.traveler_profile
        FormClass = TravelerProfileForm
        template = "profiles/traveler_edit.html"

    if request.method == "POST":
        form = FormClass(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("pages:profile")
    else:
        form = FormClass(instance=profile)

    return render(request, template, {"form": form, "profile": profile})