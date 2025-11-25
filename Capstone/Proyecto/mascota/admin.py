from django.contrib import admin
from django.utils.html import format_html
from .models import Mascota


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    """
    Admin completo para Mascotas.
    Los administradores pueden ver, crear, editar y eliminar mascotas.
    """

    list_display = (
        'id',
        'nombre',
        'especie',
        'raza',
        'sexo',
        'dueno_nombre',
        'edad_aproximada',
        'foto_thumbnail',
        'creado'
    )

    list_filter = ('especie', 'sexo', 'creado')

    search_fields = (
        'nombre',
        'especie',
        'raza',
        'DUENO__username',
        'DUENO__first_name',
        'DUENO__last_name'
    )

    autocomplete_fields = ['DUENO']

    readonly_fields = (
        'id',
        'creado',
        'actualizado',
        'foto_preview'
    )

    fieldsets = (
        ('Información Básica', {
            'fields': ('id', 'DUENO', 'nombre', 'especie', 'raza')
        }),
        ('Detalles', {
            'fields': ('sexo', 'fecha_nacimiento', 'notas')
        }),
        ('Foto', {
            'fields': ('foto_preview', 'foto'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )

    # Paginación
    list_per_page = 25

    # Ordenamiento
    ordering = ('-creado',)

    def dueno_nombre(self, obj):
        """Muestra el nombre completo del dueño"""
        if obj.DUENO.first_name and obj.DUENO.last_name:
            return f"{obj.DUENO.get_full_name()} ({obj.DUENO.username})"
        return obj.DUENO.username
    dueno_nombre.short_description = 'Dueño'

    def edad_aproximada(self, obj):
        """Calcula la edad aproximada de la mascota"""
        if not obj.fecha_nacimiento:
            return "Desconocida"

        from datetime import date
        today = date.today()
        edad = today.year - obj.fecha_nacimiento.year

        # Ajustar si aún no ha cumplido años este año
        if today.month < obj.fecha_nacimiento.month or \
           (today.month == obj.fecha_nacimiento.month and today.day < obj.fecha_nacimiento.day):
            edad -= 1

        if edad == 0:
            # Calcular meses
            meses = (today.year - obj.fecha_nacimiento.year) * 12 + today.month - obj.fecha_nacimiento.month
            if meses < 0:
                meses = 0
            return f"{meses} meses" if meses != 1 else "1 mes"

        return f"{edad} años" if edad != 1 else "1 año"
    edad_aproximada.short_description = 'Edad'

    def foto_thumbnail(self, obj):
        """Muestra una miniatura de la foto en la lista"""
        if obj.foto:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.foto.url
            )
        return "Sin foto"
    foto_thumbnail.short_description = 'Foto'

    def foto_preview(self, obj):
        """Muestra la foto completa en el detalle"""
        if obj.foto:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 400px; border-radius: 10px;" />',
                obj.foto.url
            )
        return "Sin foto"
    foto_preview.short_description = 'Vista previa'

    # PERMISOS: ADMIN PUEDE TODO
    def has_add_permission(self, request):
        """Administradores pueden crear mascotas"""
        return request.user.is_staff or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """Administradores pueden editar mascotas"""
        return request.user.is_staff or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """Administradores pueden eliminar mascotas"""
        return request.user.is_staff or request.user.is_superuser

    class Media:
        css = {
            'all': ('admin/css/mascota_admin.css',)
        }
