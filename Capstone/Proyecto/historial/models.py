from django.conf import settings
from django.db import models
from django.utils import timezone

# Import directo; este proyecto define app 'mascota' con modelo Mascota
from mascota.models import Mascota


class EventoClinico(models.Model):
    """
    Entrada del historial clínico de una mascota.

    Registra eventos como vacunas, controles, tratamientos, cirugías, etc.
    - 'veterinario' guarda el usuario que realiza o registra la atención.
      Puede ser null si el registro lo ingresó staff a pedido (sin vet asignado).
    """

    # Tipos de evento: mantener string corto para simpleza y filtros
    VACUNA = "VACUNA"
    CONTROL = "CONTROL"
    TRATAMIENTO = "TRATAMIENTO"
    CIRUGIA = "CIRUGIA"
    OTRO = "OTRO"
    TIPOS = [
        (VACUNA, "Vacuna"),
        (CONTROL, "Control"),
        (TRATAMIENTO, "Tratamiento"),
        (CIRUGIA, "Cirugía"),
        (OTRO, "Otro"),
    ]

    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.CASCADE,
        related_name="eventos_clinicos",
        help_text="Mascota a la que corresponde el evento."
    )

    tipo = models.CharField(max_length=16, choices=TIPOS, default=CONTROL)
    fecha = models.DateField(default=timezone.now, help_text="Fecha en que ocurrió el evento.")
    titulo = models.CharField(max_length=120, help_text="Título corto: 'Vacuna Rabia', 'Control anual', etc.")
    descripcion = models.TextField(blank=True)

    veterinario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="eventos_registrados",
        help_text="Usuario veterinario que realizó/registró el evento (si aplica)."
    )

    archivo = models.FileField(
        upload_to="historial_adjuntos/",
        null=True, blank=True,
        help_text="Opcional: adjuntar documento (PDF, imagen, etc.)."
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha", "-id"]
        indexes = [
            models.Index(fields=["mascota", "fecha"]),
            models.Index(fields=["tipo"]),
        ]

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.titulo} — {self.mascota.nombre}"

    # Validación sencilla de dominio: fecha no futura extrema
    def clean(self):
        from django.core.exceptions import ValidationError
        super().clean()
        # Permitir fecha=Hoy o pasado; si es muy futura no tiene sentido
        if self.fecha and self.fecha > timezone.now().date():
            # Se permite 1 día de tolerancia si el usuario está adelantado — eliminar si no se desea.
            if (self.fecha - timezone.now().date()).days > 1:
                raise ValidationError("La fecha del evento no debe ser futura.")
