from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from panel.services import notificar_vet
from cuentas.models import Perfil
from cuentas.mixins import SoloStaffMixin
from django.views.generic import TemplateView, ListView
from django.contrib.auth import get_user_model

from cuentas.models import Perfil
from mascota.models import Mascota
from citas.models import Cita
from clinicas.models import Clinica


User = get_user_model()
def es_staff(user):  # decorador rápido
    return user.is_staff or user.is_superuser

class DashboardView(SoloStaffMixin, TemplateView):
    template_name = "panel/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        vets_qs = (Perfil.objects
                   .filter(rol="VET", vet_estado="PENDIENTE")
                   .select_related("user")
                   .order_by("-id"))  

        ctx["usuarios_total"] = User.objects.count()
        ctx["vets_pendientes"] = vets_qs                
        ctx["vets_pendientes_count"] = vets_qs.count()   
        ctx["mascotas_total"] = Mascota.objects.count()
        ctx["clinicas_total"] = Clinica.objects.count()
        ctx["citas_pendientes"] = Cita.objects.filter(estado="PENDIENTE").count()
        ctx["citas_confirmadas"] = Cita.objects.filter(estado="CONFIRMADA").count()
        ctx["citas_completadas"] = Cita.objects.filter(estado="COMPLETADA").count()
        return ctx

class VetsPendientesListView(SoloStaffMixin, ListView):
    template_name = "panel/vets_pendientes.html"
    context_object_name = "pendientes"

    def get_queryset(self):
        return (Perfil.objects
                .filter(rol="VET", vet_estado="PENDIENTE")
                .select_related("user")
                .order_by("-id"))

@user_passes_test(es_staff)
def aprobar_vet(request, perfil_id):
    perfil = get_object_or_404(Perfil, pk=perfil_id)
    perfil.vet_estado = "APROBADO"
    perfil.save(update_fields=["vet_estado"])
    notificar_vet(perfil.user.email, True, perfil.user.get_username())
    messages.success(request, f"Veterinario {perfil.user.username} aprobado y notificado.")
    return redirect(reverse("panel:vets_pendientes"))

@user_passes_test(es_staff)
def rechazar_vet(request, perfil_id):
    perfil = get_object_or_404(Perfil, pk=perfil_id)
    perfil.vet_estado = "RECHAZADO"
    perfil.save(update_fields=["vet_estado"])
    notificar_vet(perfil.user.email, False, perfil.user.get_username())
    messages.info(request, f"Veterinario {perfil.user.username} rechazado y notificado.")
    return redirect(reverse("panel:vets_pendientes"))