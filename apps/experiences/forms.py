from django import forms
from .models import Experience


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = [
            "category",
            "title",
            "description",
            "image",
            "price",
            "duration_minutes",
            "max_people",
            "location",
            "tags",
            "is_active",
        ]
