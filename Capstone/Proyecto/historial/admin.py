# historial/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import EventoClinico


@admin.register(EventoClinico)
class EventoClinicoAdmin(admin.ModelAdmin):
    """
    Admin básico para revisar y gestionar eventos clínicos.
    Permite buscar, filtrar y ver el historial médico de cada mascota.
    """
    
    # Columnas que se muestran en la lista
    list_display = (
        "id",
        "mascota_info",
        "tipo_badge",
        "titulo",
        "fecha",
        "veterinario_info",
        "creado_en",
    )
    
    # Búsqueda
    search_fields = (
        "titulo",
        "descripcion",
        "mascota__nombre",
        "veterinario__username",
    )
    
    # Filtros
    list_filter = (
        "tipo",
        "fecha",
        "creado_en",
        "veterinario",
    )
    
    # Organización del formulario
    fieldsets = (
        ("Información Principal", {
            "fields": ("mascota", "tipo", "fecha", "titulo")
        }),
        ("Detalles Médicos", {
            "fields": ("descripcion", "veterinario", "archivo")
        }),
        ("Auditoría", {
            "fields": ("creado_en", "actualizado_en"),
            "classes": ("collapse",),
        }),
    )
    
    # Solo lectura
    readonly_fields = ("creado_en", "actualizado_en")
    
    # Ordenamiento
    ordering = ("-fecha", "-id")
    
    # Paginación
    list_per_page = 25
    
    # ========================================================================
    # MÉTODOS DE VISUALIZACIÓN
    # ========================================================================
    
    def mascota_info(self, obj):
        """Muestra mascota con dueño"""
        dueno = obj.mascota.dueno.username
        return f"{obj.mascota.nombre} ({dueno})"
    mascota_info.short_description = "Mascota / Dueño"
    
    def tipo_badge(self, obj):
        """Muestra tipo de evento con color"""
        colores = {
            "VACUNA": "purple",
            "CONTROL": "blue",
            "TRATAMIENTO": "orange",
            "CIRUGIA": "red",
            "OTRO": "gray",
        }
        color = colores.get(obj.tipo, "gray")
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_tipo_display()
        )
    tipo_badge.short_description = "Tipo"
    
    def veterinario_info(self, obj):
        """Muestra veterinario o 'N/A'"""
        if obj.veterinario:
            return obj.veterinario.username
        return "—"
    veterinario_info.short_description = "Veterinario"