# historial/urls.py
from django.urls import path
from .views import EventoClinicoList, EventoClinicoDetail, EventoClinicoCreate, EventoClinicoUpdate, EventoClinicoDelete

app_name = "historial"

urlpatterns = [
    path("mascota/<int:mascota_pk>/", EventoClinicoList.as_view(), name="lista"),
    path("evento/<int:pk>/", EventoClinicoDetail.as_view(), name="detalle"),
    path("mascota/<int:mascota_pk>/nuevo/", EventoClinicoCreate.as_view(), name="crear"),
    path("evento/<int:pk>/editar/", EventoClinicoUpdate.as_view(), name="editar"),
    path("evento/<int:pk>/eliminar/", EventoClinicoDelete.as_view(), name="eliminar"),
]
