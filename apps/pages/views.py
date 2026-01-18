from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from apps.profiles.forms import GuideProfileForm, TravelerProfileForm
from django.db.models import Count, Q, Sum

from apps.experiences.models import Experience, Category
from apps.bookings.models import Booking

from decimal import Decimal
from django.utils import timezone
from datetime import timedelta


def home_view(request):
    return render(request, "pages/home.html")


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

    # KPI 1: experiencias activas del guía
    experiences_qs = Experience.objects.filter(guide=request.user, is_active=True)
    experiences_count = experiences_qs.count()

    # bookings del guía (por sus experiencias)
    guide_bookings_qs = Booking.objects.filter(experience__guide=request.user)

    # KPI 2: reservas últimos 30 días (usa created_at, no date)
    bookings_30d = guide_bookings_qs.filter(created_at__date__gte=since).count()

    # KPI 3: pendientes
    pending = guide_bookings_qs.filter(status=Booking.Status.PENDING).count()

    # KPI 4: ingresos estimados 30d (solo ACCEPTED)
    revenue_30d = (
        guide_bookings_qs.filter(
            status=Booking.Status.ACCEPTED,
            created_at__date__gte=since,
        ).aggregate(total=Sum("total_price"))["total"]
        or Decimal("0.00")
    )

    # contador “no vistos” en el botón
    unseen_guide_bookings = guide_bookings_qs.filter(seen_by_guide=False).count()

    # tabla de reservas recientes
    recent_bookings = (
        guide_bookings_qs.select_related("experience", "traveler")
        .order_by("-created_at")[:8]
    )

    kpis = {
        "experiences": experiences_count,
        "bookings_30d": bookings_30d,
        "pending": pending,
        "revenue_30d": revenue_30d,
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

    return render(
        request,
        "pages/traveler_dashboard.html",
        {
            "categories": categories,
            "top_experiences": top_experiences,
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