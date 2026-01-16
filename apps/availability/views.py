from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from core.decorators import guide_required
from apps.experiences.models import Experience
from .forms import ExperienceAvailabilityForm, AvailabilityBlockForm
from .models import ExperienceAvailability, AvailabilityBlock


@guide_required
def availability_manage(request, experience_id: int):
    experience = get_object_or_404(Experience, pk=experience_id, guide=request.user)

    availability, _ = ExperienceAvailability.objects.get_or_create(experience=experience)

    if request.method == "POST":
        form = ExperienceAvailabilityForm(request.POST, instance=availability)
        if form.is_valid():
            form.save()
            messages.success(request, "Disponibilidad actualizada.")
            return redirect("availability:manage", experience_id=experience.pk)
    else:
        # precargar weekdays como strings para el widget
        initial = {"weekdays": [str(x) for x in (availability.weekdays or [])]}
        form = ExperienceAvailabilityForm(instance=availability, initial=initial)

    block_form = AvailabilityBlockForm()
    # Query directa => Pylance OK
    blocks = AvailabilityBlock.objects.filter(availability=availability).order_by("date")

    return render(
        request,
        "availability/manage.html",
        {
            "experience": experience,
            "availability": availability,
            "form": form,
            "block_form": block_form,
            "blocks": blocks,
        },
    )


@guide_required
def add_block(request, experience_id: int):
    experience = get_object_or_404(Experience, pk=experience_id, guide=request.user)
    availability, _ = ExperienceAvailability.objects.get_or_create(experience=experience)

    if request.method == "POST":
        form = AvailabilityBlockForm(request.POST)
        if form.is_valid():
            block = form.save(commit=False)
            block.availability = availability
            try:
                block.save()
                messages.success(request, "Fecha bloqueada.")
            except Exception:
                messages.error(request, "Esa fecha ya estaba bloqueada.")

    return redirect("availability:manage", experience_id=experience.pk)


@guide_required
def delete_block(request, block_id: int):
    block = get_object_or_404(
        AvailabilityBlock,
        pk=block_id,
        availability__experience__guide=request.user,
    )
    experience_id = block.availability.experience.pk
    block.delete()
    messages.success(request, "Bloqueo eliminado.")
    return redirect("availability:manage", experience_id=experience_id)
