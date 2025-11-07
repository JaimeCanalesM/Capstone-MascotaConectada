# historial/urls.py
from django.urls import path
from .views import EventoClinicoList, EventoClinicoDetail, EventoClinicoCreate, EventoClinicoUpdate, EventoClinicoDelete

app_name = "historial"

urlpatterns = [
    path("", EventoClinicoList.as_view(), name="lista"),
    path("<int:pk>/", EventoClinicoDetail.as_view(), name="detalle"),
    path("nuevo/", EventoClinicoCreate.as_view(), name="crear"),
    path("<int:pk>/editar/", EventoClinicoUpdate.as_view(), name="editar"),
    path("<int:pk>/eliminar/", EventoClinicoDelete.as_view(), name="eliminar"),
]
