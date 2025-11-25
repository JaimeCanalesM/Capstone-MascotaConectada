from django.contrib import admin
from django.utils.html import format_html
from .models import Solicitud


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'usuario', 'tipo_badge', 'asunto_corto', 'estado_badge',
        'prioridad_badge', 'creada_en'
    )
    list_filter = ('estado', 'prioridad', 'tipo', 'creada_en')
    search_fields = ('asunto', 'descripcion', 'usuario__username', 'usuario__email')
    readonly_fields = ('creada_en', 'actualizada_en', 'resuelta_en')
    date_hierarchy = 'creada_en'

    fieldsets = (
        ('Información General', {
            'fields': ('usuario', 'tipo', 'asunto', 'descripcion', 'mascota', 'archivo_adjunto')
        }),
        ('Gestión', {
            'fields': ('estado', 'prioridad', 'respuesta_admin')
        }),
        ('Fechas', {
            'fields': ('creada_en', 'actualizada_en', 'resuelta_en'),
            'classes': ('collapse',)
        }),
    )

    actions = ['marcar_en_revision', 'marcar_resuelta', 'marcar_rechazada', 'cambiar_prioridad_alta']

    def asunto_corto(self, obj):
        return obj.asunto[:60] + '...' if len(obj.asunto) > 60 else obj.asunto
    asunto_corto.short_description = 'Asunto'

    def tipo_badge(self, obj):
        colores = {
            'EDITAR_MASCOTA': 'info',
            'ELIMINAR_MASCOTA': 'danger',
            'PROBLEMA_TECNICO': 'warning',
            'CONSULTA_GENERAL': 'primary',
            'CAMBIO_DATOS': 'info',
            'REPORTE_USUARIO': 'danger',
            'SUGERENCIA': 'success',
            'OTRO': 'secondary'
        }
        return format_html(
            '<span class="badge bg-{}" style="font-size: 0.8em;">{}</span>',
            colores.get(obj.tipo, 'secondary'),
            obj.get_tipo_display()
        )
    tipo_badge.short_description = 'Tipo'

    def estado_badge(self, obj):
        colores = {
            'PENDIENTE': 'warning',
            'EN_REVISION': 'info',
            'RESUELTA': 'success',
            'RECHAZADA': 'danger'
        }
        iconos = {
            'PENDIENTE': '⏳',
            'EN_REVISION': '👁️',
            'RESUELTA': '✅',
            'RECHAZADA': '❌'
        }
        return format_html(
            '<span class="badge bg-{}">{} {}</span>',
            colores.get(obj.estado, 'secondary'),
            iconos.get(obj.estado, ''),
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'

    def prioridad_badge(self, obj):
        colores = {
            'BAJA': 'secondary',
            'MEDIA': 'primary',
            'ALTA': 'warning',
            'URGENTE': 'danger'
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colores.get(obj.prioridad, 'secondary'),
            obj.get_prioridad_display()
        )
    prioridad_badge.short_description = 'Prioridad'

    @admin.action(description='Marcar como "En revisión"')
    def marcar_en_revision(self, request, queryset):
        count = queryset.update(estado=Solicitud.ESTADO_EN_REVISION)
        self.message_user(request, f'{count} solicitud(es) marcada(s) como "En revisión".')

    @admin.action(description='Marcar como "Resuelta"')
    def marcar_resuelta(self, request, queryset):
        count = 0
        for solicitud in queryset:
            solicitud.marcar_resuelta()
            count += 1
        self.message_user(request, f'{count} solicitud(es) resuelta(s).')

    @admin.action(description='Marcar como "Rechazada"')
    def marcar_rechazada(self, request, queryset):
        count = 0
        for solicitud in queryset:
            solicitud.marcar_rechazada()
            count += 1
        self.message_user(request, f'{count} solicitud(es) rechazada(s).')

    @admin.action(description='Cambiar prioridad a ALTA')
    def cambiar_prioridad_alta(self, request, queryset):
        count = queryset.update(prioridad=Solicitud.PRIORIDAD_ALTA)
        self.message_user(request, f'{count} solicitud(es) marcada(s) con prioridad ALTA.')
