from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView

from cuentas.mixins import RolRequiredMixin
from .forms import UnifiedSignupForm
from .models import Perfil
from citas.models import Cita


# ---------------------------------------------------------------------
# LOGOUT CON MENSAJE
# ---------------------------------------------------------------------
class LogoutWithMessageView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Has cerrado sesión correctamente.")
        return super().dispatch(request, *args, **kwargs)


# ---------------------------------------------------------------------
# REGISTRO UNIFICADO
# ---------------------------------------------------------------------
class RegistroView(FormView):
    template_name = "cuentas/registro.html"
    form_class = UnifiedSignupForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user = form.save()
        perfil = getattr(user, "perfil", None)

        if perfil and perfil.rol == Perfil.ROL_VET:
            messages.success(
                self.request,
                "Cuenta creada correctamente. "
                "La solicitud de veterinario quedó en revisión. "
                "Un administrador validará tus datos."
            )
        else:
            messages.success(self.request, "Cuenta creada correctamente. Ya puedes iniciar sesión.")

        return super().form_valid(form)


# ---------------------------------------------------------------------
# REDIRECCIÓN POST-LOGIN
# ---------------------------------------------------------------------
@login_required
def redireccion_post_login(request):
    perfil = getattr(request.user, "perfil", None)

    if not perfil:
        return redirect("core:index")

    # Dueño → home
    if perfil.rol == Perfil.ROL_DUENO:
        return redirect("core:index")

    # Veterinario
    if perfil.rol == Perfil.ROL_VET:
        if perfil.vet_estado == Perfil.VET_PENDIENTE:
            messages.info(
                request,
                "Tu cuenta de veterinario aún está en revisión por un administrador."
            )
        return redirect("core:index")

    # Staff o cualquier otro → home
    return redirect("core:index")


# ---------------------------------------------------------------------
# PERFIL DEL USUARIO (DUENO o VET)
# ---------------------------------------------------------------------
@login_required
def perfil(request):
    perfil = getattr(request.user, "perfil", None)

    contexto = {
        "perfil": perfil,
        "user": request.user,
    }
    return render(request, "cuentas/perfil.html", contexto)


# ---------------------------------------------------------------------
# CITAS ATENDIDAS (solo Veterinarios o Staff)
# ---------------------------------------------------------------------
class CitasAtendidasView(RolRequiredMixin, ListView):
    model = Cita
    template_name = "citas/atendidas.html"
    context_object_name = "citas"
    roles_permitidos = ("VET", "STAFF")

    def get_queryset(self):
        qs = Cita.objects.filter(estado="COMPLETADA")
        perfil = getattr(self.request.user, "perfil", None)

        if perfil and perfil.rol == Perfil.ROL_VET:
            # Solo las citas atendidas por el veterinario actual
            qs = qs.filter(veterinario=self.request.user)

        # Tu modelo usa fecha + hora por separado
        qs = qs.order_by("-fecha", "-hora")

        return qs
