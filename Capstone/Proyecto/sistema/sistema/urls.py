from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("core.urls", "core"), namespace="core")),
    path("mascotas/", include(("mascota.urls", "mascota"), namespace="mascota")),
    path("clinicas/", include(("clinicas.urls", "clinicas"), namespace="clinicas")),
    path("citas/", include(("citas.urls", "citas"), namespace="citas")),
    path("cuentas/", include(("cuentas.urls", "cuentas"), namespace="cuentas")),
    path("accounts/", include("django.contrib.auth.urls")),  # ← login/logout/reset
]

# Servir archivos de media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
