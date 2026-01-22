from django import forms
from apps.availability.services import is_date_available
from .models import Booking
from django.utils import timezone


class BookingForm(forms.ModelForm):
    def __init__(self, *args, experience=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.experience = experience
        self.fields["preferred_language"].choices = [("", "Selecciona un idioma")] + list(self.fields["preferred_language"].choices)
        self.fields["preferred_language"].required = True
        self.fields["pickup_notes"].label = "Lugar de encuentro / recogida"
        self.fields["pickup_notes"].help_text = "Minibus: hotel/zona. Vehículo propio/a pie/bici: dónde quedas con el guía."

    class Meta:
        model = Booking
        fields = ["date", "adults", "children", "infants", "transport_mode", "pickup_notes", "preferred_language", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Opcional: alergias, ritmo, restricciones, necesidades, etc."}),
            "pickup_notes": forms.TextInput(attrs={"placeholder": "Hotel, calle, punto exacto (si minibus: hotel/zona)"}),
        }

    def clean(self):
            cleaned = super().clean()

            adults = cleaned.get("adults") or 0
            children = cleaned.get("children") or 0
            infants = cleaned.get("infants") or 0

            if adults <= 0:
                self.add_error("adults", "Debe haber al menos 1 adulto.")

            people = adults + children + infants
            if people <= 0:
                raise forms.ValidationError("Debes indicar al menos 1 persona.")

            date = cleaned.get("date")
            if date:
                today = timezone.localdate()
                if date < today:
                    self.add_error("date", "No puedes reservar en una fecha pasada.")
                
            if not cleaned.get("preferred_language"):
                self.add_error("preferred_language", "Selecciona el idioma preferido para la experiencia.")

            # Disponibilidad
            if self.experience and date:
                ok, msg = is_date_available(self.experience, date, people)
                if not ok:
                    self.add_error("date", msg)

            # Pickup requerido si necesita minibus
            transport_mode = cleaned.get("transport_mode")
            pickup_notes = (cleaned.get("pickup_notes") or "").strip()

            transport_mode = cleaned.get("transport_mode")
            pickup_notes = (cleaned.get("pickup_notes") or "").strip()

            if transport_mode == Booking.TransportMode.MINIBUS:
                if not pickup_notes:
                    self.add_error(
                        "pickup_notes",
                        "Si necesitas minibus, indica tu hotel/zona para coordinar la recogida."
                    )
            else:
                if not pickup_notes:
                    self.add_error(
                        "pickup_notes",
                        "Indica dónde quieres quedar con el guía (hotel, calle, punto exacto)."
                    )

            return cleaned



class BookingDecisionForm(forms.ModelForm):
    require_pickup_time = False
    require_guide_response = False

    class Meta:
        model = Booking
        fields = ["pickup_time", "meeting_point", "guide_response"]
        widgets = {
            "pickup_time": forms.TimeInput(attrs={"type": "time"}),
            "meeting_point": forms.TextInput(attrs={"placeholder": "Ej: Lobby Hotel X / Parking Y"}),
            "guide_response": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()

        pickup_time = cleaned.get("pickup_time")
        meeting_point = (cleaned.get("meeting_point") or "").strip()
        guide_response = (cleaned.get("guide_response") or "").strip()
        if self.require_guide_response and not guide_response:
            self.add_error("guide_response", "Indica un motivo para rechazar la reserva.")

        # Si se acepta: pickup_time obligatorio
        if self.require_pickup_time and not pickup_time:
            self.add_error(
                "pickup_time",
                "Indica la hora de recogida/encuentro para aceptar la reserva."
            )

        # Si se acepta: al menos meeting_point o guide_response
        if self.require_pickup_time:
            if not meeting_point and not guide_response:
                # Puedes elegir dónde mostrarlo:
                # 1) error general:
                raise forms.ValidationError(
                    "Para aceptar, indica al menos el punto de encuentro o un mensaje para el viajero."
                )
                # 2) o si prefieres errores por campo:
                # self.add_error("meeting_point", "Indica el punto o añade un mensaje.")
                # self.add_error("guide_response", "Indica el punto o añade un mensaje.")
        return cleaned


class BookingChangeRequestForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["date", "adults", "children", "infants", "transport_mode",
                  "pickup_notes", "preferred_language", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, booking=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.booking = booking

    def clean(self):
        cleaned = super().clean()

        # mismas validaciones que BookingForm
        adults = cleaned.get("adults") or 0
        children = cleaned.get("children") or 0
        infants = cleaned.get("infants") or 0
        people = adults + children + infants

        if adults <= 0:
            self.add_error("adults", "Debe haber al menos 1 adulto.")
        if people <= 0:
            raise forms.ValidationError("Debes indicar al menos 1 persona.")

        date = cleaned.get("date")
        if date and date < timezone.localdate():
            self.add_error("date", "No puedes reservar en una fecha pasada.")

        # disponibilidad con exclude_booking_id
        if self.booking and date:
            ok, msg = is_date_available(
                self.booking.experience,
                date,
                people,
                exclude_booking_id=self.booking.id,
            )
            if not ok:
                self.add_error("date", msg)

        return cleaned

