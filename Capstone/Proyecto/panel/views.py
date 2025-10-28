# panel/views.py
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

User = get_user_model()

# Import local de Cita para evitar dependencias circulares si el panel crece
from citas.models import Cita

"""
Vistas del panel propio (sin admin de Django).
- Requiere staff o superuser.
- Incluye métricas y gestión de citas (asignar veterinario, cambiar estado).
"""

@method_decorator(staff_member_required, name="dispatch")
class DashboardView(View):
    """
    Panel principal con métricas de alto nivel y accesos rápidos.
    """
    template_name = "panel/dashboard.html"

    def get(self, request):
        # Métricas base
        total_usuarios = User.objects.count()
        total_duenos = User.objects.filter(perfil__rol="DUENO").count()
        total_vets = User.objects.filter(perfil__rol="VET").count()
        total_vets_pend = User.objects.filter(perfil__rol="VET", perfil__vet_estado="PENDIENTE").count()

        # Métricas de citas
        citas_total = Cita.objects.count()
        citas_pend = Cita.objects.filter(estado="PENDIENTE").count()
        citas_conf = Cita.objects.filter(estado="CONFIRMADA").count()
        citas_comp = Cita.objects.filter(estado="COMPLETADA").count()
        citas_canc = Cita.objects.filter(estado="CANCELADA").count()

        ctx = {
            "total_usuarios": total_usuarios,
            "total_duenos": total_duenos,
            "total_vets": total_vets,
            "total_vets_pend": total_vets_pend,
            "citas_total": citas_total,
            "citas_pend": citas_pend,
            "citas_conf": citas_conf,
            "citas_comp": citas_comp,
            "citas_canc": citas_canc,
        }
        return render(request, self.template_name, ctx)


@method_decorator(staff_member_required, name="dispatch")
class CitasPanelListView(View):
    """
    Listado de todas las citas para staff/superuser, con filtros básicos.
    Permite asignar veterinario y cambiar estado vía POST en la misma vista.
    """
    template_name = "panel/citas.html"

    def get(self, request):
        qs = Cita.objects.select_related("mascota", "dueno", "veterinario")
        estado = request.GET.get("estado", "").strip()
        buscar = request.GET.get("q", "").strip()
        vet_id = request.GET.get("vet", "").strip()

        if estado:
            qs = qs.filter(estado=estado)
        if vet_id.isdigit():
            qs = qs.filter(veterinario_id=int(vet_id))
        if buscar:
            qs = qs.filter(
                Q(mascota__nombre__icontains=buscar) |
                Q(dueno__username__icontains=buscar) |
                Q(motivo__icontains=buscar)
            )

        vets = User.objects.filter(perfil__rol="VET", perfil__vet_estado="APROBADO").order_by("username")
        estados = [("PENDIENTE","Pendiente"), ("CONFIRMADA","Confirmada"),
                   ("COMPLETADA","Completada"), ("CANCELADA","Cancelada")]

        ctx = {"citas": qs.order_by("-fecha_hora")[:200], "vets": vets, "estados": estados,
               "f_estado": estado, "f_buscar": buscar, "f_vet": vet_id}
        return render(request, self.template_name, ctx)

    def post(self, request):
        """
        Acciones:
        - action=asignar_vet & cita_id & vet_id
        - action=cambiar_estado & cita_id & estado
        """
        action = request.POST.get("action")
        cita_id = request.POST.get("cita_id")

        cita = get_object_or_404(Cita, pk=cita_id)

        if action == "asignar_vet":
            vet_id = request.POST.get("vet_id")
            if not vet_id:
                messages.error(request, "Debe seleccionar un veterinario.")
                return redirect(reverse("panel:citas"))
            vet = get_object_or_404(User, pk=vet_id, perfil__rol="VET", perfil__vet_estado="APROBADO")
            cita.veterinario = vet
            cita.save(update_fields=["veterinario"])
            messages.success(request, f"Veterinario asignado: {vet.username}.")
            return redirect(reverse("panel:citas"))

        if action == "cambiar_estado":
            estado = request.POST.get("estado")
            if estado not in ("PENDIENTE","CONFIRMADA","COMPLETADA","CANCELADA"):
                messages.error(request, "Estado inválido.")
                return redirect(reverse("panel:citas"))
            cita.estado = estado
            cita.save(update_fields=["estado"])
            messages.success(request, f"Estado actualizado a {estado.title()}.")
            return redirect(reverse("panel:citas"))

        messages.error(request, "Acción no reconocida.")
        return redirect(reverse("panel:citas"))