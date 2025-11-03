# panel/urls.py
from django.urls import path
from . import views

app_name = "panel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("vets/<int:perfil_id>/aprobar/", views.aprobar_vet, name="aprobar_vet"),
    path("vets/<int:perfil_id>/rechazar/", views.rechazar_vet, name="rechazar_vet"),
]
