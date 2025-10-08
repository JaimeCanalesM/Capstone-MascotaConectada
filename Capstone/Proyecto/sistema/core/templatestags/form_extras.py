from django import template

register = template.Library()

@register.filter(name="add_class")
def add_class(field, css):
    """
    Agrega clases CSS a un campo de formulario sin perder las existentes.
    Uso: {{ form.campo|add_class:"form-control is-invalid" }}
    """
    existing = field.field.widget.attrs.get("class", "")
    combined = (existing + " " + css).strip() if existing else css
    return field.as_widget(attrs={"class": combined})
