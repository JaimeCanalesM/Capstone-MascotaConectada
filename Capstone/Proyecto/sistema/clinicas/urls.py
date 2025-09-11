from django.urls import path
from . import views

urlpatterns = [
    path('clinicas/', views.lista_clinicas, name='lista_clinicas'),
    path('clinicas/<int:clinica_id>/', views.detalle_clinica, name='detalle_clinica'),
]