from django import forms
from .models import Clinica

class ClinicaForm(forms.ModelForm):
    class Meta:
        model = Clinica
        fields = ["nombre","direccion","telefono","email","horario","servicios","lat","lng"]
        widgets = {
            "servicios": forms.Textarea(attrs={"rows": 3}),
        }
