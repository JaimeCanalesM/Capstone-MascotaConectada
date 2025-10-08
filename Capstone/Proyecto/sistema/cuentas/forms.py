from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class MCAuthenticationForm(AuthenticationForm):
    """Añade clases Bootstrap a los campos del login sin tocar templates."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password"].widget.attrs.update({"class": "form-control"})

class MCUserCreationForm(UserCreationForm):
    """Añade clases Bootstrap a todos los campos del registro."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            css = f.widget.attrs.get("class", "")
            f.widget.attrs["class"] = (css + " form-control").strip()
