from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import UnifiedSignupForm


# ---------------------------------------------------------------------
# Logout con mensaje (Django 5 requiere POST). Redirige al home.
# ---------------------------------------------------------------------
class LogoutWithMessageView(LogoutView):
    next_page = "core:index"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(request, "Has cerrado sesión correctamente. ¡Hasta pronto! 👋")
        return response


# ---------------------------------------------------------------------
# Registro unificado: crea usuario + perfil según checkbox is_veterinario.
# - is_veterinario = True  => rol VET, estado PENDIENTE
# - is_veterinario = False => rol DUENO
# ---------------------------------------------------------------------
class RegistroView(FormView):
    template_name = "cuentas/registro.html"
    form_class = UnifiedSignupForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        form.save()
        if form.cleaned_data.get("is_veterinario"):
            messages.success(
                self.request,
                "Cuenta creada. La solicitud de veterinario quedó en revisión. "
                "Recibirá notificación al ser aprobada."
            )
        else:
            messages.success(self.request, "Cuenta creada. Ya puede iniciar sesión.")
        return super().form_valid(form)


# ---------------------------------------------------------------------
# Redirección post-login según rol del perfil.
# - Dueño => lista de mascotas
# - Veterinario => (placeholder) home por ahora; se puede apuntar a un panel.
# - Sin perfil/rol => home
# ---------------------------------------------------------------------
@login_required
def redireccion_post_login(request):
    perfil = getattr(request.user, "perfil", None)
    if perfil and getattr(perfil, "rol", None) == "DUENO":
        return redirect("mascota:lista")
    if perfil and getattr(perfil, "rol", None) == "VET":
        # TODO: cuando exista dashboard de veterinario, cambiar aquí.
        return redirect("core:index")
    return redirect("core:index")
