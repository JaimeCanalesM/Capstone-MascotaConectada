from django.contrib import admin
from .models import Clinica

@admin.register(Clinica)
class ClinicaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "direccion", "telefono", "email")
    search_fields = ("nombre", "direccion", "servicios")
    list_per_page = 25
