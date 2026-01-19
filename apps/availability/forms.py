from django import forms
from .models import ExperienceAvailability, AvailabilityBlock


WEEKDAYS = [
    ("0", "Lunes"),
    ("1", "Martes"),
    ("2", "Miércoles"),
    ("3", "Jueves"),
    ("4", "Viernes"),
    ("5", "Sábado"),
    ("6", "Domingo"),
]


class ExperienceAvailabilityForm(forms.ModelForm):
    weekdays = forms.MultipleChoiceField(
        choices=WEEKDAYS,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Si no seleccionas nada, permitirás cualquier día.",
    )

    class Meta:
        model = ExperienceAvailability
        fields = ["is_enabled", "start_date", "end_date", "daily_capacity_people", "daily_capacity_bookings", "weekdays"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


    def clean_weekdays(self):
        data = self.cleaned_data.get("weekdays", [])
        return [int(x) for x in data]


class AvailabilityBlockForm(forms.ModelForm):
    class Meta:
        model = AvailabilityBlock
        fields = ["date", "reason"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
