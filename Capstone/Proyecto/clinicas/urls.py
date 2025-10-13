from django.urls import path
from . import views

app_name = "clinicas"

urlpatterns = [
    path("", views.ClinicaList.as_view(), name="lista"),
    path("<int:pk>/", views.ClinicaDetail.as_view(), name="detalle"),
]
