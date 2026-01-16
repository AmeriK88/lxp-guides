from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.decorators import guide_required
from .forms import ExperienceForm
from .models import Experience
from django.shortcuts import get_object_or_404


def experience_list(request):
    # Público: cualquiera puede ver experiencias activas
    experiences = Experience.objects.filter(is_active=True).select_related("guide")
    return render(request, "experiences/list.html", {"experiences": experiences})


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
    exp = get_object_or_404(Experience.objects.select_related("guide"), pk=pk)
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
