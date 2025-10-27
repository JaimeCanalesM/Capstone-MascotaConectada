from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView
from cuentas.forms import MCAuthenticationForm
from cuentas.views import LogoutWithMessageView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Apps del proyecto
    path("", include(("core.urls", "core"), namespace="core")),
    path("clinicas/", include(("clinicas.urls", "clinicas"), namespace="clinicas")),
    path("mascotas/", include(("mascota.urls", "mascota"), namespace="mascota")),
    path("cuentas/", include(("cuentas.urls", "cuentas"), namespace="cuentas")),
    path("citas/", include(("citas.urls", "citas"), namespace="citas")),

    # Panel de administración propio
    path("panel/", include(("panel.urls", "panel"), namespace="panel")),

    # Auth nativa (login con form custom + resto de endpoints)
    path(
        "accounts/login/",
        LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=MCAuthenticationForm
        ),
        name="login",
    ),
    path("accounts/logout/", LogoutWithMessageView.as_view(), name="logout"),
    path("accounts/", include("django.contrib.auth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
