from django.urls import path
from . import views

urlpatterns = [
    path ('confirmar_eliminacion', views.confirmar_eliminacion, name='confirmar_eliminacion'),
    path('detalles', views.detalles, name='detalles'),
    path('lista', views.lista, name='lista'),
    path('formas', views.formas, name='formas'),
]       