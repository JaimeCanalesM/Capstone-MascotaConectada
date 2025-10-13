from django.urls import path
from . import views

app_name = 'clinicas'

urlpatterns = [
    path("", views.lista_clinicas, name="lista"),
]