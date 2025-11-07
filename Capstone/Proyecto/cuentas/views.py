from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView
from cuentas.mixins import RolRequiredMixin
from citas.models import Cita

from .forms import UnifiedSignupForm

# ---------------------------------------------------------------------
# Logout con mensaje de éxito
class LogoutWithMessageView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Has cerrado sesión correctamente.")
        return super().dispatch(request, *args, **kwargs)

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
# - Dueño => Home
# - Veterinario => Home
# - Sin perfil/rol => home
# ---------------------------------------------------------------------
@login_required
def redireccion_post_login(request):
    perfil = getattr(request.user, "perfil", None)
    if perfil and getattr(perfil, "rol", None) == "DUENO":
        return redirect("core:index")
    if perfil and getattr(perfil, "rol", None) == "VET":
        # TODO: cuando exista dashboard de veterinario, cambiar aquí.
        return redirect("core:index")
    return redirect("core:index")

@login_required
def perfil(request):
    """Vista que muestra el perfil del usuario autenticado"""
    perfil = getattr(request.user, 'perfil', None)
    
    contexto = {
        'perfil': perfil,
        'user': request.user,
    }
    return render(request, 'cuentas/perfil.html', contexto)

class CitasAtendidasView(RolRequiredMixin, ListView):
    model = Cita
    template_name = "citas/atendidas.html"
    context_object_name = "citas"
    roles_permitidos = ("VET", "STAFF")

    def get_queryset(self):
        qs = Cita.objects.filter(estado="COMPLETADA")
        perfil = getattr(self.request.user, "perfil", None)
        # Si es VET, muestra solo las suyas; si es STAFF, muestra todas
        if perfil and perfil.rol == "VET":
            qs = qs.filter(veterinario=self.request.user)
        return qs.order_by("-fecha_hora")