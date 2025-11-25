from django.conf import settings
from django.db import models

class Mascota(models.Model):
    SEXO_M = "M"
    SEXO_H = "H"
    SEXO_CHOICES = [(SEXO_M, "Macho"), (SEXO_H, "Hembra")]

    DUENO = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mascotas"
    )
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=50, default="Perro")  # Perro, Gato, etc.
    raza = models.CharField(max_length=100, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    peso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Peso en kilogramos"
    )
    foto = models.ImageField(upload_to="mascotas/", null=True, blank=True)
    notas = models.TextField(blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.nombre} ({self.especie})"
