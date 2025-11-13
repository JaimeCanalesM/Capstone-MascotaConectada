from django import forms
from django.utils import timezone
from .models import Cita

class CitaForm(forms.ModelForm):
    """
    Form de creación/edición de Cita.

    - Widget de fecha/hora: input type=datetime-local para mejor UX.
    - Filtra 'mascota' a las mascotas del dueño autenticado.
    - Valida que 'fecha_hora' sea futura.
    """

    fecha_hora = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        label="Fecha y hora",
        required=True,
    )

    class Meta:
        model = Cita
        fields = ["mascota", "clinica", "fecha_hora", "motivo", "notas"]
        widgets = {
            "mascota": forms.Select(attrs={"class": "form-select"}),
            "clinica": forms.Select(attrs={"class": "form-select"}),
            "motivo": forms.TextInput(attrs={"class": "form-control", "maxlength": 160, "placeholder": "Ej: Control de rutina"}),
            "notas": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Notas adicionales..."}),
        }

    def __init__(self, *args, **kwargs):
        """
        Espera 'user' en kwargs para filtrar las mascotas por dueño.
        """
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user and self.user.is_authenticated:
            # Filtrar mascotas por dueño (usando DUENO en mayúscula)
            qs = self.fields["mascota"].queryset
            self.fields["mascota"].queryset = qs.filter(DUENO=self.user)

    def clean_fecha_hora(self):
        fh = self.cleaned_data.get("fecha_hora")
        if fh is None:
            return fh
        # Validación: debe ser futura
        if fh < timezone.now():
            raise forms.ValidationError("La fecha/hora debe ser futura.")
        return fh