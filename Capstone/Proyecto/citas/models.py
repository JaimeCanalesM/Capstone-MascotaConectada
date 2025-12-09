from django.conf import settings
from django.db import models
from django.utils import timezone
from .querysets import CitaQuerySet
# Nota: si existe Clinica en 'clinicas', usamos FK; si no, dejamos None (y el form la omitirá)
try:
    from clinicas.models import Clinica
except Exception:
    Clinica = None  # fallback si la app no está disponible


class Cita(models.Model):
    objects = CitaQuerySet.as_manager()
    """
    Entidad de agenda (citas médicas o controles).
    - 'dueno': usuario que solicita/posee la cita.
    - 'mascota': mascota a atender (pertenece al dueño).
    - 'clinica': opcional (puede definirse luego).
    - 'veterinario': opcional (asignado tras aprobación).
    """

    # Estados
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    COMPLETADA = "COMPLETADA"
    ESTADOS = [
        (PENDIENTE, "Pendiente"),
        (CONFIRMADA, "Confirmada"),
        (CANCELADA, "Cancelada"),
        (COMPLETADA, "Completada"),
    ]

    # Relaciones principales
    dueno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="citas",
        help_text="Usuario dueño que crea/posee la cita.",
    )

    # Import tardío para evitar ciclos de import
    from mascota.models import Mascota  # type: ignore
    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.CASCADE,
        related_name="citas",
    )

    # Clínica (si el modelo existe)
    if Clinica:
        clinica = models.ForeignKey(
            Clinica, on_delete=models.SET_NULL, null=True, blank=True, related_name="citas"
        )

    # Datos de agenda
    fecha_hora = models.DateTimeField(help_text="Fecha y hora de la cita (timezone-aware).")
    motivo = models.CharField(max_length=160, help_text="Motivo breve de la cita.")
    notas = models.TextField(blank=True)

    # Veterinario asignado (opcional)
    veterinario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="citas_asignadas",
        help_text="Usuario veterinario asignado (si aplica).",
    )

    estado = models.CharField(max_length=12, choices=ESTADOS, default=PENDIENTE)

    # Trazabilidad
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_hora", "-id"]
        indexes = [
            models.Index(fields=["dueno", "fecha_hora"]),
            models.Index(fields=["estado"]),
        ]

    def __str__(self):
        pet = getattr(self.mascota, "nombre", "Mascota")
        return f"Cita({pet} @ {self.fecha_hora:%Y-%m-%d %H:%M})"

    def clean(self):
        """
        Validación de dominio:
        - No comparar si 'fecha_hora' es None (evita TypeError).
        - Si es naive y USE_TZ=True, volverla aware con la tz actual.
        - Debe ser futura (excepto si el estado es COMPLETADA).
        """
        from django.core.exceptions import ValidationError
        from django.utils.timezone import is_naive, make_aware, get_current_timezone

        # Llamar clean() de la superclase por si se sobreescribe en el futuro
        super().clean()

        # Si no hay fecha (el ModelForm se encargará de marcar requerido), no validar más aquí
        if self.fecha_hora is None:
            return

        # Normalizar a aware si viene naive y el proyecto usa zonas horarias
        if is_naive(self.fecha_hora):
            self.fecha_hora = make_aware(self.fecha_hora, get_current_timezone())

        # Validar que sea futura SOLO si el estado NO es COMPLETADA
        if self.estado != self.COMPLETADA:
            if self.fecha_hora < timezone.now():
                raise ValidationError("La fecha/hora debe ser futura.")
