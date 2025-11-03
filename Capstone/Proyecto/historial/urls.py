# historial/urls.py
from django.urls import path
from . import views

app_name = "historial"

urlpatterns = [
    path("mascota/<int:mascota_id>/", views.EventoClinicoList.as_view(), name="lista"),
    path("mascota/<int:mascota_id>/nuevo/", views.EventoClinicoCreate.as_view(), name="nuevo"),
    path("mascota/<int:mascota_id>/<int:evento_id>/", views.EventoClinicoDetail.as_view(), name="detalle"),
    path("mascota/<int:mascota_id>/<int:evento_id>/editar/", views.EventoClinicoUpdate.as_view(), name="editar"),
    path("mascota/<int:mascota_id>/<int:evento_id>/eliminar/", views.EventoClinicoDelete.as_view(), name="eliminar"),
]
