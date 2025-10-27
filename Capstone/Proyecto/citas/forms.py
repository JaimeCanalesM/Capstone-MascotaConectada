from django import forms
from django.utils import timezone
from .models import Cita

class CitaForm(forms.ModelForm):
    """
    Form de creación/edición de Cita.

    - Widget de fecha/hora: input type=datetime-local para mejor UX.
    - Filtra 'mascota' a las mascotas del dueño autenticado.
    - Valida que 'fecha_hora' sea futura (validación redundante con el modelo, pero útil para UX).
    """

    fecha_hora = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        label="Fecha y hora",
        required=True,  # explícitamente requerido
    )

    class Meta:
        model = Cita
        fields = (
            ["mascota", "clinica", "fecha_hora", "motivo", "notas"]
            if hasattr(Cita, "clinica")
            else ["mascota", "fecha_hora", "motivo", "notas"]
        )
        widgets = {
            "mascota": forms.Select(attrs={"class": "form-select"}),
            "clinica": forms.Select(attrs={"class": "form-select"}) if hasattr(Cita, "clinica") else None,
            "motivo": forms.TextInput(attrs={"class": "form-control", "maxlength": 160}),
            "notas": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        """
        Espera 'user' en kwargs para filtrar las mascotas por dueño.
        Detecta dinámicamente el nombre del FK al usuario en Mascota (p. ej. 'DUENO' o 'dueno').
        """
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user and self.user.is_authenticated:
            qs = self.fields["mascota"].queryset
            mascota_model = qs.model

            owner_field_name = None
            try:
                for f in mascota_model._meta.get_fields():
                    if getattr(f, "is_relation", False) and getattr(f, "related_model", None):
                        if f.related_model.__name__.lower() == "user":
                            owner_field_name = f.name
                            break
            except Exception:
                owner_field_name = None

            if not owner_field_name:
                # Probar nombres comunes
                try:
                    self.fields["mascota"].queryset = qs.filter(dueno=self.user)
                except Exception:
                    self.fields["mascota"].queryset = qs.filter(DUENO=self.user)
            else:
                self.fields["mascota"].queryset = qs.filter(**{owner_field_name: self.user})

    def clean_fecha_hora(self):
        fh = self.cleaned_data.get("fecha_hora")
        # Si no hay valor, dejar que el required dispare el error estándar
        if fh is None:
            return fh
        # Validación UX: debe ser futura
        if fh < timezone.now():
            raise forms.ValidationError("La fecha/hora debe ser futura.")
        return fh
