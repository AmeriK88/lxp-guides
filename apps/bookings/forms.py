from django import forms
from apps.availability.services import is_date_available
from .models import Booking


class BookingForm(forms.ModelForm):
    def __init__(self, *args, experience=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.experience = experience

    class Meta:
        model = Booking
        fields = ["date", "adults", "children", "infants", "transport_mode", "pickup_notes", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "pickup_notes": forms.TextInput(attrs={"placeholder": "Hotel, punto de encuentro, zona..."}),
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
        if self.experience and date:
            ok, msg = is_date_available(self.experience, date, people)
            if not ok:
                self.add_error("date", msg)

        return cleaned


class BookingDecisionForm(forms.ModelForm):
    require_pickup_time = False

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
        if self.require_pickup_time and not cleaned.get("pickup_time"):
            self.add_error("pickup_time", "Indica la hora de recogida/encuentro para aceptar la reserva.")
        return cleaned
