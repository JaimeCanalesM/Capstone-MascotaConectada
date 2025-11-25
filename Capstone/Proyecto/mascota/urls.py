from django.urls import path
from .views import (
    MascotaList,
    MascotaCreate,
    MascotaUpdate,
    MascotaDelete,
    MascotaDetail,
    MascotaUpdateVet
)

app_name = "mascota"

urlpatterns = [
    path("", MascotaList.as_view(), name="lista"),
    path("nueva/", MascotaCreate.as_view(), name="crear"),
    path("<int:pk>/", MascotaDetail.as_view(), name="detalle"),
    path("<int:pk>/editar/", MascotaUpdate.as_view(), name="editar"),
    path("<int:pk>/editar-medico/", MascotaUpdateVet.as_view(), name="editar_medico"),
    path("<int:pk>/eliminar/", MascotaDelete.as_view(), name="eliminar"),
]
