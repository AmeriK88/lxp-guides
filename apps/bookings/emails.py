from django.conf import settings
from django.core.mail import send_mail


def send_booking_status_email(*, to_email: str, subject: str, message: str) -> None:
    if not to_email:
        return  # si el usuario no tiene email, no rompemos
    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None) or "no-reply@lanzaxperience.com",
        recipient_list=[to_email],
        fail_silently=True,
    )
