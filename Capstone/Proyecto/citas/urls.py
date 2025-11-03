# citas/urls.py
from django.urls import path

from . import views

app_name = "citas"

urlpatterns = [
    path("", views.CitaList.as_view(), name="lista"),
    path("proximas/", views.ProximasCitas.as_view(), name="proximas"),
    path("crear/", views.CitaCreate.as_view(), name="crear"),
    path("<int:pk>/editar/", views.CitaUpdate.as_view(), name="editar"),
    path("<int:pk>/eliminar/", views.CitaDelete.as_view(), name="eliminar"),
    path("<int:pk>/completar/", views.CitaCompletar.as_view(), name="completar"),
    path("<int:pk>/a-historial/", views.CitaToHistorial.as_view(), name="a_historial"),
    path("mis-atenciones/", views.MisAtenciones.as_view(), name="mis_atenciones"),
]
