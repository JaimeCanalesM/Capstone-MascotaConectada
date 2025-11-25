from django.urls import path
from . import views

app_name = 'solicitudes'

urlpatterns = [
    path('', views.SolicitudListView.as_view(), name='lista'),
    path('nueva/', views.SolicitudCreateView.as_view(), name='crear'),
    path('<int:pk>/', views.SolicitudDetailView.as_view(), name='detalle'),
]
