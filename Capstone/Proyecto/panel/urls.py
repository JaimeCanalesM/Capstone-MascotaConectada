# panel/urls.py
from django.urls import path
from . import views
from .views import (
    DashboardView,
    VetsPendientesListView,
    SolicitudesListView,
    SolicitudDetailView,
    aprobar_vet,
    rechazar_vet,
)

app_name = "panel"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("vets/pendientes/", VetsPendientesListView.as_view(), name="vets_pendientes"),
    path("vets/<int:perfil_id>/aprobar/", views.aprobar_vet, name="aprobar_vet"),
    path("vets/<int:perfil_id>/rechazar/", views.rechazar_vet, name="rechazar_vet"),
    path("solicitudes/", SolicitudesListView.as_view(), name="solicitudes_lista"),
    path("solicitudes/<int:pk>/", SolicitudDetailView.as_view(), name="solicitud_detalle"),
]
