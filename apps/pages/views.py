from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from apps.profiles.forms import GuideProfileForm, TravelerProfileForm


def home_view(request):
    return render(request, "pages/home.html")


@login_required
def dashboard_redirect(request):
    if request.user.is_guide():
        return redirect("pages:guide_dashboard")
    return redirect("pages:traveler_dashboard")


@login_required
def guide_dashboard(request):
    return render(request, "pages/guide_dashboard.html")


@login_required
def traveler_dashboard(request):
    return render(request, "pages/traveler_dashboard.html")

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
        form = FormClass(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("pages:profile")
    else:
        form = FormClass(instance=profile)

    return render(request, template, {"form": form, "profile": profile})