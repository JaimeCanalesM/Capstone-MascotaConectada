# panel/views.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.contrib.auth import get_user_model
from mascota.models import Mascota
from citas.models import Cita
from historial.models import EventoClinico
from cuentas.models import Perfil

User = get_user_model()


def _es_admin(user):
    """
    Devuelve True si el usuario tiene permisos de administración.
    Se usa en las vistas del panel para negar acceso a usuarios normales.
    """
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
@user_passes_test(_es_admin)
def dashboard(request):
    """
    Panel de administración resumido.
    Muestra métricas básicas y pendientes de revisión.
    """
    total_usuarios = User.objects.count()
    total_mascotas = Mascota.objects.count()
    total_citas = Cita.objects.count()
    total_eventos = EventoClinico.objects.count()

    # veterinarios que se registraron como VET y están en pendiente
    vets_pendientes = Perfil.objects.filter(rol="VET", vet_estado="PENDIENTE")

    # citas completadas pero que aún no tienen entrada de historial
    citas_completadas = Cita.objects.filter(estado="COMPLETADA")
    ids_mascotas_con_evento = (
        EventoClinico.objects.values_list("mascota_id", flat=True).distinct()
    )
    citas_sin_historial = citas_completadas.exclude(mascota_id__in=ids_mascotas_con_evento)

    contexto = {
        "total_usuarios": total_usuarios,
        "total_mascotas": total_mascotas,
        "total_citas": total_citas,
        "total_eventos": total_eventos,
        "vets_pendientes": vets_pendientes,
        "citas_sin_historial": citas_sin_historial,
    }
    return render(request, "panel/dashboard.html", contexto)


@login_required
@user_passes_test(_es_admin)
def aprobar_vet(request, perfil_id):
    """
    Cambia el estado de un perfil de veterinario a APROBADO.
    """
    perfil = get_object_or_404(Perfil, pk=perfil_id, rol="VET")
    perfil.vet_estado = "APROBADO"
    perfil.save(update_fields=["vet_estado"])
    messages.success(request, f"Veterinario '{perfil.user.username}' aprobado.")
    return redirect("panel:dashboard")


@login_required
@user_passes_test(_es_admin)
def rechazar_vet(request, perfil_id):
    """
    Cambia el estado de un perfil de veterinario a RECHAZADO.
    """
    perfil = get_object_or_404(Perfil, pk=perfil_id, rol="VET")
    perfil.vet_estado = "RECHAZADO"
    perfil.save(update_fields=["vet_estado"])
    messages.warning(request, f"Veterinario '{perfil.user.username}' rechazado.")
    return redirect("panel:dashboard")
