from django.urls import path
from . import views

app_name = "cuentas"

urlpatterns = [
    path("registro/dueno/", views.SignupDuenoView.as_view(), name="registro_dueno"),
    path("registro/veterinario/", views.SignupVetView.as_view(), name="registro_vet"),
    path("redireccion/", views.redireccion_post_login, name="redireccion"),
]
