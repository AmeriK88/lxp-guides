from django.conf import settings
from django.db import models

from apps.experiences.models import Experience


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        CANCELED = "canceled", "Canceled"

    experience = models.ForeignKey(
        Experience,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    traveler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
        limit_choices_to={"role": "traveler"},
    )

    date = models.DateField()
    people = models.PositiveIntegerField(default=1)

    # Snapshot económico (para que el precio no cambie si editas la experience)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # Tracking de notificaciones “no vistas”
    seen_by_traveler = models.BooleanField(default=True)
    seen_by_guide = models.BooleanField(default=True)

    # Mensajes
    notes = models.TextField(blank=True)  # mensaje del viajero al guía
    guide_response = models.TextField(blank=True)  # respuesta del guía al aceptar/rechazar

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["date"]),
        ]

    def __str__(self):
        return f"Booking({self.experience.title}) - {self.traveler.username} - {self.status}"
