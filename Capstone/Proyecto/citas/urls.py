from django.urls import path
from . import views

app_name = "citas"

urlpatterns = [
    path("", views.CitaList.as_view(), name="lista"),
    path("crear/", views.CitaCreate.as_view(), name="crear"),
    path("<int:pk>/", views.CitaDetail.as_view(), name="detalle"),
    path("<int:pk>/editar/", views.CitaUpdate.as_view(), name="editar"),
    path("<int:pk>/eliminar/", views.CitaDelete.as_view(), name="eliminar"),
]
