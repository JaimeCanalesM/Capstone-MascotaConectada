from django import forms
from .models import Mascota

def add_bs_classes(fields):
    for f in fields.values():
        if isinstance(f.widget, (forms.CheckboxInput, forms.RadioSelect, forms.CheckboxSelectMultiple)):
            continue
        css = f.widget.attrs.get("class", "")
        f.widget.attrs["class"] = (css + " form-control").strip()

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ["nombre", "especie", "raza", "sexo", "fecha_nacimiento", "foto", "notas"]
        widgets = {
            "sexo": forms.Select(attrs={"class": "form-select"}),
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "notas": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Firulais"}),
            "especie": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Perro"}),
            "raza": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Labrador"}),
            "foto": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bs_classes(self.fields)
        # Asegura select bootstrap
        self.fields["sexo"].widget.attrs["class"] = "form-select"