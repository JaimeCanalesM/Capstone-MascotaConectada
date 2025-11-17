from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import TemplateView, ListView
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncWeek, TruncYear
from django.db.models.functions import ExtractMonth, ExtractYear, ExtractWeek

from panel.services import notificar_vet
from cuentas.models import Perfil
from cuentas.mixins import SoloStaffMixin
from mascota.models import Mascota
from citas.models import Cita
from clinicas.models import Clinica
from historial.models import EventoClinico


User = get_user_model()


def es_staff(user):
    """Función para user_passes_test: solo staff o superuser."""
    return user.is_staff or user.is_superuser


class DashboardView(TemplateView):
    template_name = "panel/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # MÉTRICAS DIRECTAS
        ctx["total_usuarios"] = User.objects.count()
        ctx["total_mascotas"] = Mascota.objects.count()
        ctx["total_citas"] = Cita.objects.count()
        ctx["total_eventos"] = EventoClinico.objects.count()

        # VETERINARIOS PENDIENTES
        ctx["vets_pendientes"] = (
            Perfil.objects
            .filter(rol="VET", vet_estado="PENDIENTE")
            .select_related("user")
        )

        # HISTORIAL DE USUARIOS
        usuarios = User.objects.all()

        # IMPORTANTE: convertimos a list() para que json_script pueda serializar
        ctx["usuarios_por_mes"] = list(
            usuarios
            .annotate(anio=ExtractYear("date_joined"), mes=ExtractMonth("date_joined"))
            .values("anio", "mes")
            .annotate(total=Count("id"))
            .order_by("anio", "mes")
        )

        ctx["usuarios_por_semana"] = list(
            usuarios
            .annotate(anio=ExtractYear("date_joined"), semana=ExtractWeek("date_joined"))
            .values("anio", "semana")
            .annotate(total=Count("id"))
            .order_by("anio", "semana")
        )

        ctx["usuarios_por_anio"] = list(
            usuarios
            .annotate(anio=ExtractYear("date_joined"))
            .values("anio")
            .annotate(total=Count("id"))
            .order_by("anio")
        )

        # PROMEDIO DE MASCOTAS POR USUARIO
        total_usuarios = max(User.objects.count(), 1)
        total_mascotas = Mascota.objects.count()
        ctx["promedio_mascotas"] = round(total_mascotas / total_usuarios, 2)

        # USUARIOS POR ROL
        ctx["total_duenos"] = Perfil.objects.filter(rol="DUENO").count()
        ctx["total_veterinarios"] = Perfil.objects.filter(rol="VET").count()
        ctx["total_veterinarios_aprobados"] = Perfil.objects.filter(
            rol="VET", vet_estado="APROBADO"
        ).count()
        ctx["total_veterinarios_pendientes"] = Perfil.objects.filter(
            rol="VET", vet_estado="PENDIENTE"
        ).count()

        return ctx


class VetsPendientesListView(SoloStaffMixin, ListView):
    template_name = "panel/vets_pendientes.html"
    context_object_name = "pendientes"

    def get_queryset(self):
        return (
            Perfil.objects
            .filter(rol="VET", vet_estado="PENDIENTE")
            .select_related("user")
            .order_by("-id")
        )


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
