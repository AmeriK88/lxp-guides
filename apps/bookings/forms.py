from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["date", "people", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class BookingDecisionForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["guide_response"]
        widgets = {
            "guide_response": forms.Textarea(attrs={"rows": 3}),
        }
