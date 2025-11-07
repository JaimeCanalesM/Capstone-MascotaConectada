from django.urls import path
from .views import (
    CitaList, CitaDetail, CitaCreate, CitaUpdate, CitaDelete,
    CitasAtendidasView,  # 👈 añade este import
)

app_name = "citas"

urlpatterns = [
    path("", CitaList.as_view(), name="lista"),
    path("<int:pk>/", CitaDetail.as_view(), name="detalle"),
    path("nueva/", CitaCreate.as_view(), name="crear"),
    path("<int:pk>/editar/", CitaUpdate.as_view(), name="editar"),
    path("<int:pk>/eliminar/", CitaDelete.as_view(), name="eliminar"),
    path("atendidas/", CitasAtendidasView.as_view(), name="mis_atenciones"),
]
