from django.urls import path
from .views import RegistroView, redireccion_post_login

app_name = "cuentas"

urlpatterns = [
    path("registro/", RegistroView.as_view(), name="registro"),
    path("redireccion/", redireccion_post_login, name="redireccion"),
]
