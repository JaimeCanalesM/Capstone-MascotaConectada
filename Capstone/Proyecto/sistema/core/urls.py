from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('nosotros', views.nosotros, name='nosotros'),
    path('contacto', views.contacto, name='contacto'),
    path('privacidad_terminos', views.privacidad_terminos, name='privacidad_terminos'),
]