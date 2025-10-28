# panel/urls.py
from django.urls import path
from .views import DashboardView, CitasPanelListView

app_name = "panel"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("citas/", CitasPanelListView.as_view(), name="citas"),
]
