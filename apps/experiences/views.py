from django.contrib import messages
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render

from core.decorators import guide_required
from apps.bookings.models import Booking
from .forms import ExperienceForm
from .models import Category, Experience


def experience_list(request):
    # Público: solo experiencias activas de guías verificados
    experiences = (
        Experience.objects.filter(
            is_active=True,
            guide__guide_profile__verification_status="verified",
        )
        .select_related("guide", "category")
    )

    categories = Category.objects.all()

    # Filtros por querystring
    q = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    max_duration = request.GET.get("max_duration", "").strip()
    sort = request.GET.get("sort", "recent").strip()

    if q:
        experiences = experiences.filter(
            Q(title__icontains=q)
            | Q(description__icontains=q)
            | Q(location__icontains=q)
            | Q(tags__icontains=q)
            | Q(guide__username__icontains=q)
            | Q(category__name__icontains=q)
        )

    if category_slug:
        experiences = experiences.filter(category__slug=category_slug)

    if min_price:
        try:
            experiences = experiences.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            experiences = experiences.filter(price__lte=float(max_price))
        except ValueError:
            pass

    if max_duration:
        try:
            experiences = experiences.filter(duration_minutes__lte=int(max_duration))
        except ValueError:
            pass

    # Ordenación
    if sort == "price_asc":
        experiences = experiences.order_by("price", "-created_at")
    elif sort == "price_desc":
        experiences = experiences.order_by("-price", "-created_at")
    elif sort == "duration_asc":
        experiences = experiences.order_by("duration_minutes", "-created_at")
    elif sort == "duration_desc":
        experiences = experiences.order_by("-duration_minutes", "-created_at")
    elif sort == "popular":
        experiences = experiences.annotate(
            bookings_count=Count(
                "bookings",
                filter=Q(bookings__status__in=[Booking.Status.PENDING, Booking.Status.ACCEPTED]),
            )
        ).order_by("-bookings_count", "-created_at")
    else:
        experiences = experiences.order_by("-created_at")

    context = {
        "experiences": experiences,
        "categories": categories,
        "filters": {
            "q": q,
            "category": category_slug,
            "min_price": min_price,
            "max_price": max_price,
            "max_duration": max_duration,
            "sort": sort,
        },
    }
    return render(request, "experiences/list.html", context)


@guide_required
def experience_create(request):
    if request.method == "POST":
        form = ExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.guide = request.user
            exp.save()
            messages.success(request, "Experiencia creada correctamente.")
            return redirect("experiences:list")
    else:
        form = ExperienceForm()

    return render(request, "experiences/create.html", {"form": form})


def experience_detail(request, pk):
    exp = get_object_or_404(
        Experience.objects.select_related("guide", "category"),
        pk=pk,
    )
    return render(request, "experiences/detail.html", {"exp": exp})


@guide_required
def experience_edit(request, pk):
    exp = get_object_or_404(Experience, pk=pk, guide=request.user)

    if request.method == "POST":
        form = ExperienceForm(request.POST, instance=exp)
        if form.is_valid():
            form.save()
            messages.success(request, "Experiencia actualizada.")
            return redirect("experiences:detail", pk=exp.pk)
    else:
        form = ExperienceForm(instance=exp)

    return render(request, "experiences/edit.html", {"form": form, "exp": exp})


@guide_required
def experience_delete(request, pk):
    exp = get_object_or_404(Experience, pk=pk, guide=request.user)

    if request.method == "POST":
        exp.delete()
        messages.success(request, "Experiencia eliminada.")
        return redirect("experiences:list")

    return render(request, "experiences/delete.html", {"exp": exp})
