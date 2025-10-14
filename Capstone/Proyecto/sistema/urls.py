from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView
from cuentas.forms import MCAuthenticationForm
from cuentas.views import LogoutWithMessageView  # si ya lo tienes

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("core.urls", "core"), namespace="core")),
    path("clinicas/", include(("clinicas.urls", "clinicas"), namespace="clinicas")),

    # Login con form personalizado (clases Bootstrap)
    path(
        "accounts/login/",
        LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=MCAuthenticationForm
        ),
        name="login",
    ),

    # Logout con mensaje (opcional, si lo tienes)
    path("accounts/logout/", LogoutWithMessageView.as_view(), name="logout"),

    # resto de auth (password reset, etc.)
    path("accounts/", include("django.contrib.auth.urls")),
    path("cuentas/", include(("cuentas.urls", "cuentas"), namespace="cuentas")),
]
