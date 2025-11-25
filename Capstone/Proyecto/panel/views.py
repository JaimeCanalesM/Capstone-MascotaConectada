from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import TemplateView, ListView
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Case, When, IntegerField
from django.db.models.functions import TruncMonth, TruncWeek, TruncYear
from django.db.models.functions import ExtractMonth, ExtractYear, ExtractWeek
from django.utils import timezone
from datetime import timedelta

from panel.services import notificar_vet
from cuentas.models import Perfil
from cuentas.mixins import SoloStaffMixin
from mascota.models import Mascota
from citas.models import Cita
from clinicas.models import Clinica
from historial.models import EventoClinico
from solicitudes.models import Solicitud


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

        # CITAS POR ESTADO (ÚLTIMOS 6 MESES)
        hace_6_meses = timezone.now() - timedelta(days=180)
        citas_6_meses = Cita.objects.filter(creado_en__gte=hace_6_meses)

        ctx["citas_completadas"] = citas_6_meses.filter(estado="COMPLETADA").count()
        ctx["citas_canceladas"] = citas_6_meses.filter(estado="CANCELADA").count()
        ctx["citas_pendientes"] = citas_6_meses.filter(estado="PENDIENTE").count()
        ctx["citas_confirmadas"] = citas_6_meses.filter(estado="CONFIRMADA").count()

        # MASCOTAS POR ESPECIE
        ctx["mascotas_por_especie"] = list(
            Mascota.objects
            .values("especie")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        # RANKING DE VETERINARIOS (por número de citas atendidas)
        ctx["ranking_veterinarios"] = list(
            Cita.objects
            .filter(veterinario__isnull=False, estado="COMPLETADA")
            .values("veterinario__username", "veterinario__first_name", "veterinario__last_name")
            .annotate(total_atendidas=Count("id"))
            .order_by("-total_atendidas")[:10]  # Top 10
        )

        # ANÁLISIS PREDICTIVO: Probabilidad de registro de mascota
        total_usuarios_con_mascota = User.objects.filter(mascotas__isnull=False).distinct().count()
        total_usuarios = max(User.objects.count(), 1)
        ctx["probabilidad_registro_mascota"] = round((total_usuarios_con_mascota / total_usuarios) * 100, 2)

        # Más estadísticas predictivas
        ctx["usuarios_con_mascota"] = total_usuarios_con_mascota
        ctx["usuarios_sin_mascota"] = total_usuarios - total_usuarios_con_mascota

        # Promedio de citas por mascota
        total_citas = Cita.objects.count()
        total_mascotas_activas = max(Mascota.objects.count(), 1)
        ctx["promedio_citas_por_mascota"] = round(total_citas / total_mascotas_activas, 2)

        # SOLICITUDES
        ctx["total_solicitudes"] = Solicitud.objects.count()
        ctx["solicitudes_pendientes"] = Solicitud.objects.filter(estado=Solicitud.ESTADO_PENDIENTE).count()
        ctx["solicitudes_en_revision"] = Solicitud.objects.filter(estado=Solicitud.ESTADO_EN_REVISION).count()
        ctx["solicitudes_resueltas"] = Solicitud.objects.filter(estado=Solicitud.ESTADO_RESUELTA).count()
        ctx["solicitudes_urgentes"] = Solicitud.objects.filter(
            prioridad=Solicitud.PRIORIDAD_URGENTE,
            estado__in=[Solicitud.ESTADO_PENDIENTE, Solicitud.ESTADO_EN_REVISION]
        ).count()

        # SOLICITUDES RECIENTES (últimas 10)
        ctx["solicitudes_recientes"] = Solicitud.objects.select_related('usuario', 'mascota').order_by('-creada_en')[:10]

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


# SOLICITUDES MANAGEMENT VIEWS

class SolicitudesListView(SoloStaffMixin, ListView):
    """Vista para gestionar solicitudes en el panel de administración"""
    model = Solicitud
    template_name = "panel/solicitudes_lista.html"
    context_object_name = "solicitudes"
    paginate_by = 20

    def get_queryset(self):
        qs = Solicitud.objects.select_related('usuario', 'mascota').order_by('-creada_en')

        # Filter by estado
        estado = self.request.GET.get('estado')
        if estado:
            qs = qs.filter(estado=estado)

        # Filter by prioridad
        prioridad = self.request.GET.get('prioridad')
        if prioridad:
            qs = qs.filter(prioridad=prioridad)

        # Filter by tipo
        tipo = self.request.GET.get('tipo')
        if tipo:
            qs = qs.filter(tipo=tipo)

        # Search
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(asunto__icontains=q) |
                Q(descripcion__icontains=q) |
                Q(usuario__username__icontains=q) |
                Q(usuario__email__icontains=q)
            )

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Current filters
        ctx['estado_actual'] = self.request.GET.get('estado', '')
        ctx['prioridad_actual'] = self.request.GET.get('prioridad', '')
        ctx['tipo_actual'] = self.request.GET.get('tipo', '')
        ctx['q'] = self.request.GET.get('q', '')

        # Statistics
        ctx['total_solicitudes'] = Solicitud.objects.count()
        ctx['pendientes'] = Solicitud.objects.filter(estado=Solicitud.ESTADO_PENDIENTE).count()
        ctx['en_revision'] = Solicitud.objects.filter(estado=Solicitud.ESTADO_EN_REVISION).count()
        ctx['resueltas'] = Solicitud.objects.filter(estado=Solicitud.ESTADO_RESUELTA).count()
        ctx['rechazadas'] = Solicitud.objects.filter(estado=Solicitud.ESTADO_RECHAZADA).count()

        return ctx


from django.views.generic import DetailView

class SolicitudDetailView(SoloStaffMixin, DetailView):
    """Vista para ver una solicitud en detalle dentro del panel de administración"""
    model = Solicitud
    template_name = "panel/solicitud_detalle.html"
    context_object_name = "solicitud"
