from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Perfil

# Utilidades para aplicar clases Bootstrap automáticamente
def add_bs_classes(fields, select_fields=None):
    if select_fields is None:
        select_fields = []
    for name, field in fields.items():
        if isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.CheckboxSelectMultiple)):
            continue
        cls = "form-select" if name in select_fields else "form-control"
        field.widget.attrs["class"] = (field.widget.attrs.get("class", "") + " " + cls).strip()


# Login con estilos Bootstrap
class MCAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bs_classes(self.fields)


# FORMULARIO DE REGISTRO UNIFICADO
# - Si marca "Soy veterinario": exige registro, clínica y licencia médica
class UnifiedSignupForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=30, required=False)
    last_name = forms.CharField(label="Apellido", max_length=30, required=False)
    email = forms.EmailField(label="Email", required=True)

    is_veterinario = forms.BooleanField(
        label="Soy veterinario (requiere aprobación)",
        required=False,
        help_text="Seleccionar solo si ejerce como veterinario."
    )

    vet_registro = forms.CharField(
        label="Registro profesional",
        max_length=100,
        required=False
    )

    vet_clinica = forms.CharField(
        label="Clínica/centro",
        max_length=200,
        required=False
    )

    # Archivo obligatorio si es veterinario
    licencia_medica = forms.FileField(
        label="Licencia médica / Título profesional",
        required=False,
        help_text="Subir PDF, JPG o PNG. Obligatorio si marca 'Soy veterinario'."
    )

    class Meta:
        model = User
        fields = (
            "username", "first_name", "last_name", "email",
            "password1", "password2",
            "is_veterinario", "vet_registro", "vet_clinica",
            "licencia_medica",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bs_classes(self.fields)

        # Ajustar checkbox
        self.fields["is_veterinario"].widget.attrs["class"] = "form-check-input"

        # Ajustar input file
        self.fields["licencia_medica"].widget.attrs["class"] = "form-control"

    # VALIDACIONES
    def clean(self):
        cleaned = super().clean()
        is_vet = cleaned.get("is_veterinario")

        reg = cleaned.get("vet_registro", "").strip()
        clinica = cleaned.get("vet_clinica", "").strip()
        archivo = cleaned.get("licencia_medica")

        # Si es veterinario, se obliga a completar todo
        if is_vet:

            # Registro profesional
            if not reg:
                self.add_error("vet_registro", "Debes ingresar tu número de registro profesional.")

            # Clínica
            if not clinica:
                self.add_error("vet_clinica", "Debes indicar la clínica o centro donde ejercen.")

            # Archivo obligatorio
            if not archivo:
                self.add_error("licencia_medica", "Debes subir tu licencia médica o título profesional.")
            else:
                # Validación de tipo
                ext = archivo.name.lower().split(".")[-1]
                if ext not in ["pdf", "jpg", "jpeg", "png"]:
                    self.add_error("licencia_medica", "Formato inválido. Solo PDF, JPG o PNG.")

                # Validación de tamaño (máx 5 MB)
                if archivo.size > 5 * 1024 * 1024:
                    self.add_error("licencia_medica", "El archivo no debe exceder 5MB.")

        return cleaned

    # SAVE()
    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            perfil = getattr(user, "perfil", None)
            if not perfil:
                perfil = Perfil.objects.create(user=user)

            if self.cleaned_data.get("is_veterinario"):

                perfil.rol = Perfil.ROL_VET
                perfil.vet_estado = Perfil.VET_PENDIENTE

                perfil.vet_registro = self.cleaned_data.get("vet_registro", "")
                perfil.vet_clinica = self.cleaned_data.get("vet_clinica", "")

                # Guardar archivo de licencia médica
                archivo = self.cleaned_data.get("licencia_medica")
                if archivo:
                    perfil.licencia_medica = archivo

            else:
                perfil.rol = Perfil.ROL_DUENO
                perfil.vet_estado = None
                perfil.vet_registro = ""
                perfil.vet_clinica = ""
                perfil.licencia_medica = None

            perfil.save()

        return user
