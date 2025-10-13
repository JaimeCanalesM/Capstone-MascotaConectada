from django.urls import path
from . import views   # ← ¡esto es clave!

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("nosotros/", views.nosotros, name="nosotros"),
    path("contacto/", views.contacto, name="contacto"),
    path("privacidad-terminos/", views.privacidad_terminos, name="privacidad_terminos"),
]
