from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import Cita


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    """
    Interfaz de administración para Citas.
    Permite gestionar, filtrar y buscar citas fácilmente.
    """
    
    # Columnas que se muestran en la lista
    list_display = (
        "id",
        "mascota_info",
        "fecha_hora_formateada",
        "estado_badge",
        "veterinario_info",
        "creado_en",
    )
    
    # Campos que se pueden usar para búsqueda
    search_fields = (
        "mascota__nombre",
        "dueno__username",
        "dueno__email",
        "motivo",
        "veterinario__username",
    )
    
    # Campos que se pueden filtrar
    list_filter = (
        "estado",
        "fecha_hora",
        "creado_en",
        "veterinario",
        "clinica",
    )
    
    # Campos organizados en el formulario de edición
    fieldsets = (
        ("Información Principal", {
            "fields": ("dueno", "mascota", "fecha_hora", "motivo")
        }),
        ("Clínica y Veterinario", {
            "fields": ("clinica", "veterinario"),
            "classes": ("collapse",)
        }),
        ("Estado y Notas", {
            "fields": ("estado", "notas")
        }),
        ("Auditoría", {
            "fields": ("creado_en", "actualizado_en"),
            "classes": ("collapse",),
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ("creado_en", "actualizado_en")
    
    # Ordenamiento por defecto
    ordering = ("-fecha_hora",)
    
    # Cantidad de registros por página
    list_per_page = 25
    
    # ACCIONES PERSONALIZADAS

    actions = [
        "marcar_confirmada",
        "marcar_completada_con_evento",
        "marcar_cancelada"
    ]
    
    def marcar_confirmada(self, request, queryset):
        """Acción: marcar citas como CONFIRMADA"""
        updated = queryset.update(estado="CONFIRMADA")
        messages.success(request, f"✅ {updated} cita(s) marcada(s) como CONFIRMADA")
    marcar_confirmada.short_description = "✓ Marcar como CONFIRMADA"
    
    def marcar_completada_con_evento(self, request, queryset):
        """
        Acción: marcar como COMPLETADA Y crear automáticamente el evento clínico.
        Esta es la acción más importante - une ambas acciones en una.
        """
        from historial.models import EventoClinico
        
        created_eventos = 0
        updated_citas = 0
        
        for cita in queryset:
            # 1. Marcar cita como COMPLETADA
            if cita.estado != "COMPLETADA":
                cita.estado = "COMPLETADA"
                cita.save()
                updated_citas += 1
            
            # 2. Crear evento clínico si no existe
            evento_existe = EventoClinico.objects.filter(
                mascota=cita.mascota,
                fecha=cita.fecha_hora.date(),
                tipo="CONTROL"
            ).exists()
            
            if not evento_existe:
                try:
                    EventoClinico.objects.create(
                        mascota=cita.mascota,
                        tipo="CONTROL",
                        fecha=cita.fecha_hora.date(),
                        titulo=f"Cita completada: {cita.motivo}",
                        descripcion=cita.notas or "Sin notas adicionales",
                        veterinario=cita.veterinario
                    )
                    created_eventos += 1
                    print(f"EventoClinico creado para Cita {cita.id}")
                except Exception as e:
                    print(f"Error creando EventoClinico para Cita {cita.id}: {e}")
        
        # Mensaje de confirmación
        msg = f"✅ {updated_citas} cita(s) completada(s) y {created_eventos} evento(s) clínico(s) creado(s)"
        messages.success(request, msg)
    marcar_completada_con_evento.short_description = "Marcar COMPLETADA + Crear Evento Clínico"
    
    def marcar_cancelada(self, request, queryset):
        """Acción: marcar citas como CANCELADA"""
        updated = queryset.update(estado="CANCELADA")
        messages.success(request, f" {updated}cita(s) marcada(s) como CANCELADA")
    marcar_cancelada.short_description = "✗ Marcar como CANCELADA"
    
 
    # MÉTODOS DE VISUALIZACIÓN PERSONALIZADA
  
    
    def mascota_info(self, obj):
        """Muestra nombre de mascota con propietario"""
        return f"{obj.mascota.nombre} ({obj.dueno.username})"
    mascota_info.short_description = "Mascota / Dueño"
    
    def fecha_hora_formateada(self, obj):
        """Muestra fecha y hora formateadas"""
        return obj.fecha_hora.strftime("%d/%m/%Y %H:%M")
    fecha_hora_formateada.short_description = "Fecha y Hora"
    
    def estado_badge(self, obj):
        """Muestra estado con color de fondo"""
        colores = {
            "PENDIENTE": "orange",
            "CONFIRMADA": "blue",
            "COMPLETADA": "green",
            "CANCELADA": "red",
        }
        color = colores.get(obj.estado, "gray")
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.estado
        )
    estado_badge.short_description = "Estado"
    
    def veterinario_info(self, obj):
        """Muestra veterinario o 'Sin asignar'"""
        if obj.veterinario:
            return f"{obj.veterinario.username}"
        return "Sin asignar"
    veterinario_info.short_description = "Veterinario"
    

    # PERMISOS Y VALIDACIONES

    
    def get_readonly_fields(self, request, obj=None):
        """
        Si es una cita existente, algunos campos son de solo lectura.
        """
        readonly = list(self.readonly_fields)
        if obj:  # Editando existente
            readonly.extend(["dueno", "mascota"])  # No cambiar dueño ni mascota
        return readonly