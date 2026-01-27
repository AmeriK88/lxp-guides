from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.core.exceptions import ValidationError


class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.Role.choices)

    class Meta:
        model = User
        fields = ("username", "email", "role", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data["role"]
        user.email = (user.email or "").lower()
        if commit:
            user.save()
        return user
    
DELETE_PHRASE = "ELIMINAR PERMANENTEMENTE"

class DeleteAccountForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label="Entiendo que esta acción es permanente y desactiva mi cuenta."
    )
    phrase = forms.CharField(
        required=True,
        label=f'Escribe "{DELETE_PHRASE}" para confirmar',
        help_text="Esto evita eliminaciones accidentales.",
        widget=forms.TextInput(attrs={"autocomplete": "off"})
    )

    def clean_phrase(self):
        value = (self.cleaned_data.get("phrase") or "").strip().upper()
        if value != DELETE_PHRASE:
            raise ValidationError(f'Debes escribir exactamente: {DELETE_PHRASE}')
        return value
