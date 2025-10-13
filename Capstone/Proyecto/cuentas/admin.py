from django.contrib import admin
from .models import Perfil

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "rol", "vet_estado", "vet_registro", "vet_clinica", "creado", "actualizado")
    list_filter = ("rol", "vet_estado")
    search_fields = ("user__username", "user__email", "vet_registro", "vet_clinica")

    actions = ["aprobar_veterinarios", "rechazar_veterinarios"]

    @admin.action(description="Aprobar veterinarios seleccionados")
    def aprobar_veterinarios(self, request, queryset):
        queryset.filter(rol=Perfil.ROL_VET).update(vet_estado=Perfil.VET_APROBADO)

    @admin.action(description="Rechazar veterinarios seleccionados")
    def rechazar_veterinarios(self, request, queryset):
        queryset.filter(rol=Perfil.ROL_VET).update(vet_estado=Perfil.VET_RECHAZADO)
