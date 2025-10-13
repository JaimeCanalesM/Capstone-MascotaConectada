from django.urls import path
from . import views

app_name = 'mascota'

urlpatterns = [
    path ('confirmar_eliminacion', views.confirmar_eliminacion, name='confirmar_eliminacion'),
    path('detalles', views.detalles, name='detalles'),
    path('lista', views.lista, name='lista'),
    path("crear/", views.crear_mascota, name="crear"),
    path('formas', views.formas, name='formas'),
    path("crear/", views.crear_mascota, name="crear"),
]       