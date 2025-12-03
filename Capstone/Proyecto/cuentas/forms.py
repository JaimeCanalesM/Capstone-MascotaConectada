from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Perfil
from .validators import validar_rut_chileno, formatear_rut

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

    vet_rut = forms.CharField(
        label="RUT",
        max_length=12,
        required=False,
        help_text="Formato: 12.345.678-9"
    )

    vet_registro = forms.CharField(
        label="RUN (Rol Único Nacional del veterinario)",
        max_length=100,
        required=False,
        help_text="Ingrese su RUN profesional"
    )

    vet_clinica = forms.CharField(
        label="Clínica/Centro (Opcional)",
        max_length=200,
        required=False,
        help_text="Indique la clínica o centro donde ejerce, si aplica"
    )

    # Archivo obligatorio si es veterinario
    licencia_medica = forms.FileField(
        label="Título de médico veterinario",
        required=False,
        help_text="Subir PDF, JPG o PNG del título profesional. Obligatorio si marca 'Soy veterinario'."
    )

    class Meta:
        model = User
        fields = (
            "username", "first_name", "last_name", "email",
            "password1", "password2",
            "is_veterinario", "vet_rut", "vet_registro", "vet_clinica",
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

        rut = cleaned.get("vet_rut", "").strip()
        reg = cleaned.get("vet_registro", "").strip()
        clinica = cleaned.get("vet_clinica", "").strip()
        archivo = cleaned.get("licencia_medica")

        # Si es veterinario, se obliga a completar todo
        if is_vet:

            # RUT obligatorio
            if not rut:
                self.add_error("vet_rut", "Debes ingresar tu RUT.")
            else:
                # Validar formato y dígito verificador del RUT
                try:
                    validar_rut_chileno(rut)
                    # Formatear RUT automáticamente
                    cleaned["vet_rut"] = formatear_rut(rut)
                except ValidationError as e:
                    self.add_error("vet_rut", e.message)

            # RUN (Registro profesional)
            if not reg:
                self.add_error("vet_registro", "Debes ingresar tu RUN profesional.")

            # Clínica (opcional, no se valida)

            # Archivo obligatorio (título de médico veterinario)
            if not archivo:
                self.add_error("licencia_medica", "Debes subir tu título de médico veterinario.")
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

                perfil.vet_rut = self.cleaned_data.get("vet_rut", "")
                perfil.vet_registro = self.cleaned_data.get("vet_registro", "")
                perfil.vet_clinica = self.cleaned_data.get("vet_clinica", "")

                # Guardar archivo del título de médico veterinario
                archivo = self.cleaned_data.get("licencia_medica")
                if archivo:
                    perfil.licencia_medica = archivo

            else:
                perfil.rol = Perfil.ROL_DUENO
                perfil.vet_estado = None
                perfil.vet_rut = ""
                perfil.vet_registro = ""
                perfil.vet_clinica = ""
                perfil.licencia_medica = None

            perfil.save()

        return user


# FORMULARIO DE EDICIÓN DE PERFIL
class EditarPerfilForm(forms.ModelForm):
    """Formulario para editar información personal y foto de perfil"""

    first_name = forms.CharField(
        label="Nombre",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    last_name = forms.CharField(
        label="Apellido",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        label="Correo Electrónico",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    foto_perfil = forms.ImageField(
        label="Foto de Perfil",
        required=False,
        help_text="Sube una imagen JPG, JPEG o PNG (máx. 2MB)",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )

    eliminar_foto = forms.BooleanField(
        label="Eliminar foto actual",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    # Campos de contraseña opcionales
    current_password = forms.CharField(
        label="Contraseña Actual",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Solo si deseas cambiar la contraseña'}),
        help_text="Ingresa tu contraseña actual solo si deseas cambiarla"
    )

    new_password = forms.CharField(
        label="Nueva Contraseña",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Mínimo 8 caracteres"
    )

    confirm_password = forms.CharField(
        label="Confirmar Nueva Contraseña",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        self.perfil = kwargs.pop('perfil', None)
        super().__init__(*args, **kwargs)

    def clean_foto_perfil(self):
        foto = self.cleaned_data.get('foto_perfil')
        if foto:
            # Validar tipo de archivo
            ext = foto.name.lower().split('.')[-1]
            if ext not in ['jpg', 'jpeg', 'png']:
                raise forms.ValidationError('Solo se permiten imágenes JPG, JPEG o PNG')

            # Validar tamaño (máx 2MB)
            if foto.size > 2 * 1024 * 1024:
                raise forms.ValidationError('La imagen no debe exceder 2MB')

        return foto

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        # Si se ingresó algún campo de contraseña, validar todo
        if current_password or new_password or confirm_password:
            # Todos los campos son requeridos
            if not current_password:
                self.add_error('current_password', 'Debes ingresar tu contraseña actual')
            elif not self.instance.check_password(current_password):
                self.add_error('current_password', 'La contraseña actual es incorrecta')

            if not new_password:
                self.add_error('new_password', 'Debes ingresar una nueva contraseña')
            elif len(new_password) < 8:
                self.add_error('new_password', 'La contraseña debe tener al menos 8 caracteres')

            if not confirm_password:
                self.add_error('confirm_password', 'Debes confirmar la nueva contraseña')
            elif new_password and confirm_password and new_password != confirm_password:
                self.add_error('confirm_password', 'Las contraseñas no coinciden')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            # Cambiar contraseña si se proporcionó
            new_password = self.cleaned_data.get('new_password')
            if new_password:
                user.set_password(new_password)
                user.save()

            # Actualizar foto de perfil
            if self.perfil:
                if self.cleaned_data.get('eliminar_foto'):
                    if self.perfil.foto_perfil:
                        self.perfil.foto_perfil.delete(save=False)
                    self.perfil.foto_perfil = None
                elif self.cleaned_data.get('foto_perfil'):
                    # Eliminar foto anterior si existe
                    if self.perfil.foto_perfil:
                        self.perfil.foto_perfil.delete(save=False)
                    self.perfil.foto_perfil = self.cleaned_data['foto_perfil']

                self.perfil.save()

        return user
