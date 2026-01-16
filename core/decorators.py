from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def guide_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if not getattr(request.user, "is_guide", lambda: False)():
            messages.error(request, "Solo los guías pueden acceder a esta sección.")
            return redirect("pages:dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped
