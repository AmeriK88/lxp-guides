from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.decorators import guide_required
from .forms import ExperienceForm
from .models import Category, Experience


def experience_list(request):
    # Público: cualquiera puede ver experiencias activas
    experiences = (
        Experience.objects.filter(is_active=True)
        .select_related("guide", "category")
        .order_by("-created_at")
    )

    categories = Category.objects.all()

    # Filtros por querystring
    q = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    max_duration = request.GET.get("max_duration", "").strip()

    if q:
        experiences = experiences.filter(
            Q(title__icontains=q)
            | Q(description__icontains=q)
            | Q(location__icontains=q)
            | Q(guide__username__icontains=q)
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

    context = {
        "experiences": experiences,
        "categories": categories,
        "filters": {
            "q": q,
            "category": category_slug,
            "min_price": min_price,
            "max_price": max_price,
            "max_duration": max_duration,
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
