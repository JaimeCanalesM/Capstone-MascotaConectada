from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from cuentas.models import Perfil

# ---------------------------------------------------------------------
# Decorador: restringe acceso a staff o superuser
# ---------------------------------------------------------------------
def staff_required(view_func):
    decorated = login_required(user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func))
    return decorated

# ---------------------------------------------------------------------
# Dashboard con métricas básicas
# ---------------------------------------------------------------------
@staff_required
def dashboard(request):
    total_users = User.objects.count()
    total_duenos = Perfil.objects.filter(rol=Perfil.ROL_DUENO).count()
    total_vets = Perfil.objects.filter(rol=Perfil.ROL_VET).count()
    total_vets_pend = Perfil.objects.filter(rol=Perfil.ROL_VET, vet_estado=Perfil.VET_PENDIENTE).count()

    # Top 5 usuarios más recientes (por fecha de creación del user si existe; fallback: id)
    recientes = User.objects.order_by("-date_joined", "-id")[:5]

    ctx = {
        "total_users": total_users,
        "total_duenos": total_duenos,
        "total_vets": total_vets,
        "total_vets_pend": total_vets_pend,
        "recientes": recientes,
    }
    return render(request, "panel/dashboard.html", ctx)

# ---------------------------------------------------------------------
# Lista de veterinarios pendientes
# ---------------------------------------------------------------------
@staff_required
def veterinarios_pendientes(request):
    pendientes = Perfil.objects.select_related("user").filter(
        rol=Perfil.ROL_VET, vet_estado=Perfil.VET_PENDIENTE
    )
    return render(request, "panel/vets_pendientes.html", {"pendientes": pendientes})

# ---------------------------------------------------------------------
# Aprobar veterinario (POST)
# ---------------------------------------------------------------------
@staff_required
def veterinario_aprobar(request, user_id):
    if request.method != "POST":
        messages.error(request, "Método no permitido.")
        return redirect("panel:veterinarios_pendientes")

    perfil = get_object_or_404(Perfil, user_id=user_id, rol=Perfil.ROL_VET)
    perfil.vet_estado = Perfil.VET_APROBADO
    perfil.save(update_fields=["vet_estado"])
    messages.success(request, f"Veterinario '{perfil.user.username}' aprobado.")
    return redirect("panel:veterinarios_pendientes")

# ---------------------------------------------------------------------
# Rechazar veterinario (POST)
# ---------------------------------------------------------------------
@staff_required
def veterinario_rechazar(request, user_id):
    if request.method != "POST":
        messages.error(request, "Método no permitido.")
        return redirect("panel:veterinarios_pendientes")

    perfil = get_object_or_404(Perfil, user_id=user_id, rol=Perfil.ROL_VET)
    perfil.vet_estado = Perfil.VET_RECHAZADO
    perfil.save(update_fields=["vet_estado"])
    messages.warning(request, f"Veterinario '{perfil.user.username}' rechazado.")
    return redirect("panel:veterinarios_pendientes")
