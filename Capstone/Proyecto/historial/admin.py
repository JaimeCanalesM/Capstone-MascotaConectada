# historial/admin.py
from django.contrib import admin
from .models import EventoClinico


@admin.register(EventoClinico)
class EventoClinicoAdmin(admin.ModelAdmin):
    """
    Admin básico para revisar eventos clínicos.
    No usa autocomplete_fields para no requerir que Mascota esté registrada en admin.
    """
    list_display = ("id", "mascota", "tipo", "titulo", "fecha", "veterinario", "creado_en")
    list_filter = ("tipo", "fecha")
    search_fields = (
        "titulo",
        "descripcion",
        "mascota__nombre",
        "veterinario__username",
    )
    # Si se quiere, se puede usar raw_id_fields para no cargar muchas mascotas
    raw_id_fields = ("mascota", "veterinario")
