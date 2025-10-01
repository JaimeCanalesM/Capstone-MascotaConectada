from django.urls import path
from . import views

urlpatterns = [
    path('lista_citas/', views.lista_citas, name='lista_citas'),
    path('forma_cita/', views.forma_cita, name='forma_cita'),
    path('confirmar_eliminar_cita', views.confirmar_eliminar_cita, name='confirmar_eliminar_cita'),
]