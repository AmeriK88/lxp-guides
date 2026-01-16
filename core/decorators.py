from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def guide_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return redirect("accounts:login")

        if not user.is_guide():
            messages.error(request, "Solo los guías pueden acceder a esta sección.")
            return redirect("pages:dashboard")

        # Nuevo: verificación obligatoria
        if hasattr(user, "guide_profile"):
            if user.guide_profile.verification_status != "verified":
                messages.warning(
                    request,
                    "Tu perfil está pendiente de verificación. "
                    "No podrás publicar experiencias hasta ser aprobado."
                )
                return redirect("pages:profile")

        return view_func(request, *args, **kwargs)

    return _wrapped
