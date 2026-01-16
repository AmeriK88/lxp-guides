from django import forms
from .models import Experience


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "price",
            "duration_minutes",
            "max_people",
            "location",
            "is_active",
        ]
