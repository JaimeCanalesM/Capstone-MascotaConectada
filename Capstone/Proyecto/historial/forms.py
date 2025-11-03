from django import forms
from .models import EventoClinico
from django.contrib.auth import get_user_model

User = get_user_model()

class EventoClinicoForm(forms.ModelForm):
    """
    Form para crear/editar eventos clínicos.
    - Veterinario es opcional (staff puede cargar histórico sin vet).
    - El dropdown de veterinarios se restringe a perfil 'VET' aprobado.
    """

    class Meta:
        model = EventoClinico
        fields = ["tipo", "fecha", "titulo", "descripcion", "veterinario", "archivo"]
        widgets = {
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "titulo": forms.TextInput(attrs={"class": "form-control", "maxlength": 120}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "veterinario": forms.Select(attrs={"class": "form-select"}),
            "archivo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restringir lista de veterinarios a los aprobados
        self.fields["veterinario"].queryset = User.objects.filter(
            perfil__rol="VET", perfil__vet_estado="APROBADO"
        ).order_by("username")
        self.fields["veterinario"].required = False
