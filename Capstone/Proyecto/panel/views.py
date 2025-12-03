from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import TemplateView, ListView
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Case, When, IntegerField, Avg, Max, Min, F
from django.db.models.functions import ExtractMonth, ExtractYear, ExtractWeek, ExtractWeekDay, ExtractHour
from django.utils import timezone
from datetime import timedelta, datetime
from collections import defaultdict

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

        # Filtrar usuarios desde el 1 de octubre del año actual
        fecha_inicio_octubre = datetime(2024, 10, 1)
        usuarios_desde_octubre = usuarios.filter(date_joined__gte=fecha_inicio_octubre)

        ctx["usuarios_por_semana"] = list(
            usuarios_desde_octubre
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

        # ========================================================================
        # MINERÍA DE DATOS - ANÁLISIS AVANZADO
        # ========================================================================

        # 1. ANÁLISIS DE COHORTES - Retención de usuarios por mes de registro
        ahora = timezone.now()
        hace_30_dias = ahora - timedelta(days=30)
        hace_60_dias = ahora - timedelta(days=60)
        hace_90_dias = ahora - timedelta(days=90)
        hace_3_meses = hace_90_dias

        # Usuarios registrados en los últimos 3 meses
        cohortes = User.objects.filter(
            date_joined__gte=hace_3_meses
        ).annotate(
            anio_registro=ExtractYear('date_joined'),
            mes_registro=ExtractMonth('date_joined')
        ).values('anio_registro', 'mes_registro').annotate(
            total_registrados=Count('id'),
            activos_mes_actual=Count(
                'id',
                filter=Q(
                    mascotas__citas__creado_en__gte=hace_30_dias
                )
            )
        ).order_by('-anio_registro', '-mes_registro')[:3]

        cohorte_data = []
        meses_es = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        for cohorte in cohortes:
            if cohorte['total_registrados'] > 0:
                # Validar que tengamos año y mes válidos
                mes = cohorte.get('mes_registro')
                anio = cohorte.get('anio_registro')
                if not mes or not anio:
                    continue

                retencion = round((cohorte['activos_mes_actual'] / cohorte['total_registrados']) * 100, 1)
                mes_nombre = meses_es[mes]
                cohorte_data.append({
                    'mes': f"{mes_nombre} {anio}",
                    'registrados': cohorte['total_registrados'],
                    'activos': cohorte['activos_mes_actual'],
                    'retencion': retencion
                })

        ctx['cohortes_retencion'] = cohorte_data

        # 2. SEGMENTACIÓN RFM ADAPTADA (Recency, Frequency, Activity)
        # Clasificamos usuarios en grupos según su comportamiento

        # Calcular métricas RFA para cada usuario con mascotas
        usuarios_rfm = []
        for user in User.objects.filter(mascotas__isnull=False).distinct():
            # Recency: días desde última cita
            ultima_cita = Cita.objects.filter(
                mascota__DUENO=user
            ).order_by('-creado_en').first()

            if ultima_cita:
                dias_ultima_cita = (ahora - ultima_cita.creado_en).days
            else:
                dias_ultima_cita = 999  # Sin citas

            # Frequency: total de citas
            total_citas_usuario = Cita.objects.filter(mascota__DUENO=user).count()

            # Activity: número de mascotas registradas
            total_mascotas_usuario = Mascota.objects.filter(DUENO=user).count()

            # Clasificación
            if dias_ultima_cita <= 30 and total_citas_usuario >= 3:
                segmento = 'VIP - Activo'
            elif dias_ultima_cita <= 30:
                segmento = 'Activo Regular'
            elif dias_ultima_cita <= 90 and total_citas_usuario >= 2:
                segmento = 'Recurrente'
            elif dias_ultima_cita <= 90:
                segmento = 'En Riesgo'
            elif total_citas_usuario > 0:
                segmento = 'Inactivo'
            else:
                segmento = 'Nuevo'

            usuarios_rfm.append({
                'user_id': user.id,
                'recency': dias_ultima_cita,
                'frequency': total_citas_usuario,
                'activity': total_mascotas_usuario,
                'segmento': segmento
            })

        # Contar usuarios por segmento
        segmentos_count = defaultdict(int)
        for u in usuarios_rfm:
            segmentos_count[u['segmento']] += 1

        ctx['segmentacion_rfm'] = dict(segmentos_count)
        ctx['total_usuarios_segmentados'] = len(usuarios_rfm)

        # 3. PATRONES TEMPORALES - Análisis de días/horas con más actividad
        # Distribución de citas por día de la semana
        citas_por_dia = Cita.objects.annotate(
            dia_semana=ExtractWeekDay('fecha_hora')
        ).values('dia_semana').annotate(
            total=Count('id')
        ).order_by('dia_semana')

        dias_nombres = {
            1: 'Domingo', 2: 'Lunes', 3: 'Martes', 4: 'Miércoles',
            5: 'Jueves', 6: 'Viernes', 7: 'Sábado'
        }

        patrones_dia = []
        max_citas_dia = 1
        for item in citas_por_dia:
            patrones_dia.append({
                'dia': dias_nombres.get(item['dia_semana'], 'Desconocido'),
                'total': item['total']
            })
            max_citas_dia = max(max_citas_dia, item['total'])

        ctx['patrones_dia_semana'] = patrones_dia
        ctx['max_citas_dia'] = max_citas_dia

        # Horarios con más citas
        citas_por_hora = Cita.objects.annotate(
            hora=ExtractHour('fecha_hora')
        ).values('hora').annotate(
            total=Count('id')
        ).order_by('-total')[:3]

        horarios_pico = []
        for item in citas_por_hora:
            horarios_pico.append({
                'hora': f"{item['hora']}:00",
                'total': item['total']
            })

        ctx['horarios_pico'] = horarios_pico

        # 4. CLUSTERING DE COMPORTAMIENTO
        # Identificar grupos de usuarios según su patrón de uso

        # Cluster 1: Usuarios VIP (alta frecuencia, alta recurrencia)
        cluster_vip = len([u for u in usuarios_rfm if u['frequency'] >= 3 and u['recency'] <= 60])

        # Cluster 2: Usuarios Ocasionales (baja frecuencia, uso esporádico)
        cluster_ocasional = len([u for u in usuarios_rfm if u['frequency'] <= 2 and u['recency'] <= 180])

        # Cluster 3: Usuarios en Riesgo de Abandono (no han usado el sistema recientemente)
        cluster_riesgo = len([u for u in usuarios_rfm if u['recency'] > 90 and u['frequency'] > 0])

        # Cluster 4: Usuarios Nuevos sin actividad
        cluster_nuevos = len([u for u in usuarios_rfm if u['frequency'] == 0])

        ctx['clusters'] = {
            'vip': cluster_vip,
            'ocasional': cluster_ocasional,
            'riesgo': cluster_riesgo,
            'nuevos': cluster_nuevos
        }

        # 5. TASA DE CONVERSIÓN (de registro a primera cita)
        total_usuarios = max(User.objects.count(), 1)
        usuarios_con_citas = User.objects.filter(
            mascotas__citas__isnull=False
        ).distinct().count()

        ctx['tasa_conversion_citas'] = round((usuarios_con_citas / total_usuarios) * 100, 2)

        # 6. VALOR PROMEDIO DEL USUARIO (citas por usuario activo)
        if usuarios_con_citas > 0:
            total_citas = Cita.objects.count()
            ctx['citas_promedio_usuario_activo'] = round(total_citas / usuarios_con_citas, 2)
        else:
            ctx['citas_promedio_usuario_activo'] = 0

        # ========================================================================
        # ESTADÍSTICAS AVANZADAS Y PROBABILIDADES
        # ========================================================================

        # 1. PROBABILIDAD CONDICIONAL: P(citas mensuales | número de mascotas)
        # Calculamos la probabilidad de que un usuario con X mascotas agende al menos 1 cita al mes

        # Usuarios con mascotas que agendaron citas en el último mes
        usuarios_con_mascota_y_citas = User.objects.filter(
            mascotas__isnull=False,
            mascotas__citas__creado_en__gte=hace_30_dias
        ).distinct().count()

        total_usuarios_con_mascota = max(User.objects.filter(mascotas__isnull=False).distinct().count(), 1)

        ctx["prob_cita_mensual_dado_mascota"] = round(
            (usuarios_con_mascota_y_citas / total_usuarios_con_mascota) * 100, 2
        )

        # 2. TASA DE RETENCIÓN MENSUAL
        # Usuarios que se registraron hace 2 meses y que han tenido actividad (citas) en el último mes

        usuarios_antiguos = User.objects.filter(
            date_joined__lte=hace_60_dias
        ).count()

        usuarios_activos_recientes = User.objects.filter(
            date_joined__lte=hace_60_dias,
            mascotas__citas__creado_en__gte=hace_30_dias
        ).distinct().count()

        if usuarios_antiguos > 0:
            ctx["tasa_retencion_mensual"] = round((usuarios_activos_recientes / usuarios_antiguos) * 100, 2)
        else:
            ctx["tasa_retencion_mensual"] = 0

        # 3. DISTRIBUCIÓN DE ACTIVIDAD POR ROL CON PROBABILIDADES
        # Probabilidad de que un dueño tenga al menos 1 cita
        duenos_totales = max(Perfil.objects.filter(rol="DUENO").count(), 1)
        duenos_con_citas = Perfil.objects.filter(
            rol="DUENO",
            user__mascotas__citas__isnull=False
        ).distinct().count()

        ctx["prob_dueno_con_citas"] = round((duenos_con_citas / duenos_totales) * 100, 2)

        # Probabilidad de que un veterinario aprobado haya atendido al menos 1 cita
        vets_aprobados = max(Perfil.objects.filter(rol="VET", vet_estado="APROBADO").count(), 1)
        vets_con_citas_atendidas = Perfil.objects.filter(
            rol="VET",
            vet_estado="APROBADO",
            user__citas_asignadas__isnull=False
        ).distinct().count()

        ctx["prob_vet_con_citas_atendidas"] = round((vets_con_citas_atendidas / vets_aprobados) * 100, 2)

        # 4. TASA DE CONVERSIÓN DE VETERINARIOS
        # Porcentaje de solicitudes de veterinario que fueron aprobadas vs rechazadas
        vets_procesados = Perfil.objects.filter(
            rol="VET",
            vet_estado__in=["APROBADO", "RECHAZADO"]
        ).count()

        if vets_procesados > 0:
            ctx["tasa_aprobacion_veterinarios"] = round(
                (ctx["total_veterinarios_aprobados"] / vets_procesados) * 100, 2
            )
        else:
            ctx["tasa_aprobacion_veterinarios"] = 0

        # 5. TASA DE ENGAGEMENT DEL SISTEMA
        # Porcentaje de usuarios totales que han realizado al menos 1 acción (registro de mascota o cita)
        usuarios_activos = User.objects.filter(
            Q(mascotas__isnull=False) | Q(mascotas__citas__isnull=False)
        ).distinct().count()

        ctx["tasa_engagement"] = round((usuarios_activos / total_usuarios) * 100, 2)

        # 6. PROMEDIO DE MASCOTAS POR USUARIO ACTIVO (solo usuarios con mascotas)
        if total_usuarios_con_mascota > 0:
            ctx["promedio_mascotas_usuario_activo"] = round(total_mascotas / total_usuarios_con_mascota, 2)
        else:
            ctx["promedio_mascotas_usuario_activo"] = 0

        # 7. DISTRIBUCIÓN DE USUARIOS POR NÚMERO DE MASCOTAS
        distribucion_mascotas = {}
        for i in range(1, 6):  # De 1 a 5+ mascotas
            if i < 5:
                count = User.objects.annotate(num_mascotas=Count('mascotas')).filter(num_mascotas=i).count()
                distribucion_mascotas[f"{i}_mascota{'s' if i > 1 else ''}"] = count
            else:
                count = User.objects.annotate(num_mascotas=Count('mascotas')).filter(num_mascotas__gte=5).count()
                distribucion_mascotas["5_o_mas_mascotas"] = count

        ctx["distribucion_mascotas"] = distribucion_mascotas

        # 8. TASA DE FINALIZACIÓN DE CITAS
        # Porcentaje de citas completadas vs total de citas
        if total_citas > 0:
            citas_completadas_total = Cita.objects.filter(estado="COMPLETADA").count()
            ctx["tasa_finalizacion_citas"] = round((citas_completadas_total / total_citas) * 100, 2)
        else:
            ctx["tasa_finalizacion_citas"] = 0

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
