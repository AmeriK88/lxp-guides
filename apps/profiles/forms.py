from django import forms
from .models import GuideProfile, TravelerProfile


class GuideProfileForm(forms.ModelForm):
    class Meta:
        model = GuideProfile
        fields = [
            "display_name",
            "bio",
            "languages",
            "phone",
            "instagram",
            "website",
            "avatar",
            "guide_license_document",
            "insurance_or_registration_document",
        ]


class TravelerProfileForm(forms.ModelForm):
    # Campos del User (cuenta)
    first_name = forms.CharField(label="Nombre", required=False, max_length=150)
    last_name = forms.CharField(label="Apellidos", required=False, max_length=150)
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        model = TravelerProfile
        fields = ["display_name", "phone", "preferred_language", "country", "city"]
        labels = {
            "display_name": "Nombre público",
            "phone": "Teléfono",
            "preferred_language": "Idioma preferido",
            "country": "País",
            "city": "Ciudad",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is None:
            raise ValueError("TravelerProfileForm requires a user")
        self.user = user

        # precargar datos de User
        self.fields["first_name"].initial = user.first_name
        self.fields["last_name"].initial = user.last_name
        self.fields["email"].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=False)

        # Guardar User
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        self.user.email = self.cleaned_data["email"]

        if commit:
            self.user.save()
            profile.user = self.user
            profile.save()

        return profile
