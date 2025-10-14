from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Perfil

# ---------- util ----------

def add_bs_classes(fields, select_fields=None):
    """
    Asigna clases Bootstrap a los widgets de un form.
    - inputs: class="form-control"
    - selects (si los hay): class="form-select"
    """
    if select_fields is None:
        select_fields = []
    for name, field in fields.items():
        css = "form-select" if name in select_fields else "form-control"
        if isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.CheckboxSelectMultiple)):
            # para checks/radios no forcemos form-control
            continue
        existing = field.widget.attrs.get("class", "")
        field.widget.attrs["class"] = (existing + " " + css).strip()

# ---------- login ----------

class MCAuthenticationForm(AuthenticationForm):
    """
    AuthenticationForm con widgets Bootstrap.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bs_classes(self.fields)

# ---------- registro base ----------

class BaseSignupForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=30, required=False)
    last_name = forms.CharField(label="Apellido", max_length=30, required=False)
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bs_classes(self.fields)

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

    class Meta(BaseSignupForm.Meta):
        fields = BaseSignupForm.Meta.fields  # heredamos los campos base

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # agregamos los campos extra al form y les aplicamos clases
        self.fields["vet_registro"] = SignupVetForm.base_fields["vet_registro"]
        self.fields["vet_clinica"] = SignupVetForm.base_fields["vet_clinica"]
        add_bs_classes(self.fields)

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            perfil = getattr(user, "perfil", None)
            if not perfil:
                perfil = Perfil.objects.create(user=user)
            perfil.rol = Perfil.ROL_VET
            perfil.vet_estado = Perfil.VET_PENDIENTE
            perfil.vet_registro = self.cleaned_data.get("vet_registro", "")
            perfil.vet_clinica = self.cleaned_data.get("vet_clinica", "")
            perfil.save()
        return user
# Nota: la aprobación del vet se hará desde el admin o una vista aparte.