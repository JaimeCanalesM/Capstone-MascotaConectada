from django.urls import path
from .views import MCLoginView, registro, perfil

app_name = "cuentas"

urlpatterns = [
    path("login/", MCLoginView.as_view(), name="login"),   # opcional; fallback si navegan directo
    path("registro/", registro, name="registro"),
    path("perfil/", perfil, name="perfil"),
]
