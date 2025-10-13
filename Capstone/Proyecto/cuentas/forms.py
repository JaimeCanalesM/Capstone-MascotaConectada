from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Perfil

class BaseSignupForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=30, required=False)
    last_name = forms.CharField(label="Apellido", max_length=30, required=False)
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

class SignupDuenoForm(BaseSignupForm):
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            perfil = getattr(user, "perfil", None)
            if perfil:
                perfil.rol = Perfil.ROL_DUENO
                perfil.vet_estado = None
                perfil.vet_registro = ""
                perfil.vet_clinica = ""
                perfil.save()
            else:
                Perfil.objects.create(user=user, rol=Perfil.ROL_DUENO)
        return user

class SignupVetForm(BaseSignupForm):
    vet_registro = forms.CharField(
        label="Registro profesional", max_length=100,
        help_text="Ej: SEREMI/colegiatura"
    )
    vet_clinica = forms.CharField(
        label="Clínica/centro", max_length=200, required=False
    )

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            perfil = getattr(user, "perfil", None)
            if not perfil:
                perfil = Perfil.objects.create(user=user)

            perfil.rol = Perfil.ROL_VET
            perfil.vet_estado = Perfil.VET_PENDIENTE  # 👈 queda pendiente
            perfil.vet_registro = self.cleaned_data.get("vet_registro", "")
            perfil.vet_clinica = self.cleaned_data.get("vet_clinica", "")
            perfil.save()
        return user
