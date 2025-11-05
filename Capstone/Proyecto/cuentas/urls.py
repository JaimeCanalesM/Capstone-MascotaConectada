from django.urls import path
from .views import RegistroView, redireccion_post_login, perfil
from django.views.generic import TemplateView

app_name = "cuentas"

urlpatterns = [
    path("registro/", RegistroView.as_view(), name="registro"),
    path("redireccion/", redireccion_post_login, name="redireccion"),
    path("perfil/", perfil, name="perfil"),
]