from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView

from cuentas.mixins import RolRequiredMixin
from .forms import UnifiedSignupForm, EditarPerfilForm
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
    from mascota.models import Mascota
    from solicitudes.models import Solicitud

    perfil = getattr(request.user, "perfil", None)
    user = request.user

    # Estadísticas según rol
    estadisticas = {}

    if perfil and perfil.rol == Perfil.ROL_DUENO:
        # Dueño: mascotas, solicitudes
        estadisticas['mascotas'] = Mascota.objects.filter(DUENO=user).count()
        estadisticas['solicitudes_totales'] = Solicitud.objects.filter(usuario=user).count()
        estadisticas['solicitudes_pendientes'] = Solicitud.objects.filter(
            usuario=user,
            estado__in=['PENDIENTE', 'EN_REVISION']
        ).count()
        estadisticas['citas_proximas'] = Cita.objects.filter(
            mascota__DUENO=user,
            estado='PENDIENTE'
        ).count()

    elif perfil and perfil.rol == Perfil.ROL_VET:
        # Veterinario: citas atendidas, citas pendientes
        estadisticas['citas_completadas'] = Cita.objects.filter(
            veterinario=user,
            estado='COMPLETADA'
        ).count()
        estadisticas['citas_proximas'] = Cita.objects.filter(
            veterinario=user,
            estado='PENDIENTE'
        ).count()
        estadisticas['mascotas_atendidas'] = Mascota.objects.filter(
            eventoclinico__veterinario=user
        ).distinct().count()

    # Admin/Staff
    if user.is_staff or user.is_superuser:
        from django.contrib.auth.models import User
        estadisticas['total_usuarios'] = User.objects.count()
        estadisticas['total_mascotas'] = Mascota.objects.count()
        estadisticas['solicitudes_pendientes'] = Solicitud.objects.filter(
            estado__in=['PENDIENTE', 'EN_REVISION']
        ).count()

    contexto = {
        "perfil": perfil,
        "user": user,
        "estadisticas": estadisticas,
    }
    return render(request, "cuentas/perfil.html", contexto)


# ---------------------------------------------------------------------
# EDITAR PERFIL
# ---------------------------------------------------------------------
@login_required
def editar_perfil(request):
    from django.contrib.auth import update_session_auth_hash

    perfil = getattr(request.user, "perfil", None)

    if request.method == "POST":
        form = EditarPerfilForm(
            request.POST,
            request.FILES,
            instance=request.user,
            perfil=perfil
        )
        if form.is_valid():
            user = form.save()

            # Si se cambió la contraseña, mantener la sesión activa
            if form.cleaned_data.get('new_password'):
                update_session_auth_hash(request, user)
                messages.success(request, "Perfil y contraseña actualizados correctamente.")
            else:
                messages.success(request, "Perfil actualizado correctamente.")

            return redirect("cuentas:perfil")
    else:
        form = EditarPerfilForm(
            instance=request.user,
            perfil=perfil
        )

    contexto = {
        "form": form,
        "perfil": perfil,
    }
    return render(request, "cuentas/editar_perfil.html", contexto)


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
