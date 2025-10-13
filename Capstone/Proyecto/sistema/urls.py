from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("core.urls", "core"), namespace="core")),
    path("clinicas/", include(("clinicas.urls", "clinicas"), namespace="clinicas")),
    path("accounts/", include("django.contrib.auth.urls")),  # login/logout
    path("cuentas/", include(("cuentas.urls", "cuentas"), namespace="cuentas")), # registros + redirección
]
