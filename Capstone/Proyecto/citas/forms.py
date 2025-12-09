from django import forms
from django.utils import timezone
from .models import Cita

class CitaForm(forms.ModelForm):
    """
    Form de creación/edición de Cita.

    - Widget de fecha/hora: input type=datetime-local para mejor UX.
    - Filtra 'mascota' a las mascotas del dueño autenticado.
    - Valida que 'fecha_hora' sea futura (excepto si se marca como completada).
    """

    fecha_hora = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        label="Fecha y hora",
        required=True,
    )

    marcar_como_completada = forms.BooleanField(
        required=False,
        initial=False,
        label="Marcar como completada (la atención ya fue realizada)",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        help_text="Marca esta casilla si estás registrando una cita que ya fue atendida"
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

        # Si estamos editando una cita existente que ya está completada, pre-marcar el checkbox
        if self.instance and self.instance.pk and self.instance.estado == Cita.COMPLETADA:
            self.fields['marcar_como_completada'].initial = True

    def clean(self):
        cleaned_data = super().clean()
        fecha_hora = cleaned_data.get("fecha_hora")
        marcar_completada = cleaned_data.get("marcar_como_completada")

        # Validar que la fecha sea futura SOLO si NO se marca como completada
        if fecha_hora and not marcar_completada:
            if fecha_hora < timezone.now():
                self.add_error('fecha_hora', "La fecha/hora debe ser futura, o marca la casilla de 'completada' si la atención ya fue realizada.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Si se marcó como completada, establecer el estado
        if self.cleaned_data.get('marcar_como_completada'):
            instance.estado = Cita.COMPLETADA

        if commit:
            instance.save()

        return instance