from django.db import models

class Clinica(models.Model):
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=250, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    horario = models.CharField(max_length=200, blank=True, help_text="Ej: Lun-Vie 9:00-18:00")
    servicios = models.TextField(blank=True, help_text="Lista/descripcion de servicios")
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
