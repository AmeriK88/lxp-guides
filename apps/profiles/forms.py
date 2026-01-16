from django import forms
from .models import GuideProfile, TravelerProfile


class GuideProfileForm(forms.ModelForm):
    class Meta:
        model = GuideProfile
        fields = ["display_name", "bio", "languages", "phone", "instagram", "website"]


class TravelerProfileForm(forms.ModelForm):
    class Meta:
        model = TravelerProfile
        fields = ["display_name"]
