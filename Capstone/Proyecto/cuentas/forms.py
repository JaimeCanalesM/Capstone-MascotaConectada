from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Perfil

# ---------------------------------------------------------------------
# Utilidades para aplicar clases Bootstrap a los widgets de los forms
# ---------------------------------------------------------------------
def add_bs_classes(fields, select_fields=None):
    if select_fields is None:
        select_fields = []
    for name, field in fields.items():
        # No forzar form-control a checks y radios
        if isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.CheckboxSelectMultiple)):
            continue
        cls = "form-select" if name in select_fields else "form-control"
        field.widget.attrs["class"] = (field.widget.attrs.get("class", "") + " " + cls).strip()

# ---------------------------------------------------------------------
# Login con widgets Bootstrap (se mantiene para /accounts/login/)


class MCAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bs_classes(self.fields)

# ---------------------------------------------------------------------
# Registro unificado con checkbox "Soy veterinario"
# - Si se marca: rol = VET, vet_estado = PENDIENTE; se piden campos extra.
# - Si no: rol = DUENO
# ---------------------------------------------------------------------
class UnifiedSignupForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=30, required=False)
    last_name = forms.CharField(label="Apellido", max_length=30, required=False)
    email = forms.EmailField(label="Email", required=True)

    # Checkbox que define el rol solicitado
    is_veterinario = forms.BooleanField(
        label="Soy veterinario (requiere aprobación)",
        required=False,
        help_text="Seleccionar solo si ejerce como veterinario. Un administrador validará los datos."
    )

    # Campos visibles SOLO si marca “Soy veterinario”
    vet_registro = forms.CharField(
        label="Registro profesional",
        max_length=100,
        required=False,
        help_text="Ej: SEREMI/colegiatura. Obligatorio si marca 'Soy veterinario'."
    )
    vet_clinica = forms.CharField(
        label="Clínica/centro",
        max_length=200,
        required=False
    )

    class Meta:
        model = User
        fields = (
            "username", "first_name", "last_name", "email",
            "password1", "password2",
            "is_veterinario", "vet_registro", "vet_clinica",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bs_classes(self.fields)
        # Ajustar tipos de input y estilos complementarios
        self.fields["is_veterinario"].widget.attrs["class"] = "form-check-input"

    def clean(self):
        cleaned = super().clean()
        is_vet = cleaned.get("is_veterinario")
        reg = cleaned.get("vet_registro", "").strip()
        # Validación condicional: si es vet, se exige registro profesional
        if is_vet and not reg:
            self.add_error("vet_registro", "Obligatorio para solicitudes de veterinario.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            perfil = getattr(user, "perfil", None)
            if not perfil:
                perfil = Perfil.objects.create(user=user)

            if self.cleaned_data.get("is_veterinario"):
                # Rol veterinario queda en revisión
                perfil.rol = Perfil.ROL_VET
                perfil.vet_estado = Perfil.VET_PENDIENTE
                perfil.vet_registro = self.cleaned_data.get("vet_registro", "")
                perfil.vet_clinica = self.cleaned_data.get("vet_clinica", "")
            else:
                # Rol dueño sin revisión
                perfil.rol = Perfil.ROL_DUENO
                perfil.vet_estado = None
                perfil.vet_registro = ""
                perfil.vet_clinica = ""
            perfil.save()
        return user
