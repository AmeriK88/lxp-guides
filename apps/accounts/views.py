from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import RegisterForm
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings


def register_view(request):
    if request.user.is_authenticated:
        return redirect("pages:dashboard")


    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cuenta creada. Ya puedes iniciar sesión.")
            return redirect("accounts:login")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})



def login_view(request):
    # Si ya está logueado, fuera del login
    if request.user.is_authenticated:
        return redirect("pages:dashboard")

    # Si viene con ?next=...
    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenido de nuevo, {user.username} 👋")

                if next_url and url_has_allowed_host_and_scheme(
                    url=next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    return redirect(next_url)

                return redirect("pages:dashboard")

            # Seguridad: solo redirigir a next si es seguro
            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            return redirect("pages:dashboard")

        messages.error(request, "Credenciales incorrectas.")

    return render(request, "accounts/login.html", {"next": next_url})



@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión.")
    return redirect("accounts:login")

