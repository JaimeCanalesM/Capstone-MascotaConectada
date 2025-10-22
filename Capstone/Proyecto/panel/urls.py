from django.urls import path
from . import views

app_name = "panel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("veterinarios/pendientes/", views.veterinarios_pendientes, name="veterinarios_pendientes"),
    path("veterinarios/<int:user_id>/aprobar/", views.veterinario_aprobar, name="veterinario_aprobar"),
    path("veterinarios/<int:user_id>/rechazar/", views.veterinario_rechazar, name="veterinario_rechazar"),
]
