from django.db import models
from django.contrib.auth.models import User
from mascota.models import Mascota


class Solicitud(models.Model):
    """
    Solicitudes de usuarios/veterinarios hacia la administración
    """

    # TIPOS DE SOLICITUD
    TIPO_CHOICES = [
        ('EDITAR_MASCOTA', 'Solicitud de edición de mascota'),
        ('ELIMINAR_MASCOTA', 'Solicitud de eliminación de mascota'),
        ('PROBLEMA_TECNICO', 'Reportar problema técnico'),
        ('CONSULTA_GENERAL', 'Consulta general'),
        ('CAMBIO_DATOS', 'Solicitud de cambio de datos personales'),
        ('REPORTE_USUARIO', 'Reportar comportamiento de usuario'),
        ('SUGERENCIA', 'Sugerencia de mejora'),
        ('OTRO', 'Otro tipo de solicitud'),
    ]

    # ESTADOS
    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_EN_REVISION = 'EN_REVISION'
    ESTADO_RESUELTA = 'RESUELTA'
    ESTADO_RECHAZADA = 'RECHAZADA'

    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_EN_REVISION, 'En revisión'),
        (ESTADO_RESUELTA, 'Resuelta'),
        (ESTADO_RECHAZADA, 'Rechazada'),
    ]

    # PRIORIDADES
    PRIORIDAD_BAJA = 'BAJA'
    PRIORIDAD_MEDIA = 'MEDIA'
    PRIORIDAD_ALTA = 'ALTA'
    PRIORIDAD_URGENTE = 'URGENTE'

    PRIORIDAD_CHOICES = [
        (PRIORIDAD_BAJA, 'Baja'),
        (PRIORIDAD_MEDIA, 'Media'),
        (PRIORIDAD_ALTA, 'Alta'),
        (PRIORIDAD_URGENTE, 'Urgente'),
    ]

    # CAMPOS
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='solicitudes',
        help_text='Usuario que realiza la solicitud'
    )

    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        help_text='Tipo de solicitud'
    )

    asunto = models.CharField(
        max_length=200,
        help_text='Asunto o título de la solicitud'
    )

    descripcion = models.TextField(
        help_text='Descripción detallada de la solicitud'
    )

    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes',
        help_text='Mascota relacionada (si aplica)'
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_PENDIENTE
    )

    prioridad = models.CharField(
        max_length=10,
        choices=PRIORIDAD_CHOICES,
        default=PRIORIDAD_MEDIA,
        help_text='Prioridad asignada por el administrador'
    )

    respuesta_admin = models.TextField(
        blank=True,
        help_text='Respuesta del administrador'
    )

    archivo_adjunto = models.FileField(
        upload_to='solicitudes/',
        blank=True,
        null=True,
        help_text='Archivo adjunto (opcional)'
    )

    # TIMESTAMPS
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)
    resuelta_en = models.DateTimeField(null=True, blank=True)

    # METADATOS
    class Meta:
        ordering = ['-creada_en']
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'
        indexes = [
            models.Index(fields=['usuario', 'estado']),
            models.Index(fields=['estado', 'prioridad']),
            models.Index(fields=['creada_en']),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.usuario.username} ({self.estado})"

    def es_pendiente(self):
        return self.estado == self.ESTADO_PENDIENTE

    def es_resuelta(self):
        return self.estado == self.ESTADO_RESUELTA

    def marcar_resuelta(self):
        from django.utils import timezone
        self.estado = self.ESTADO_RESUELTA
        self.resuelta_en = timezone.now()
        self.save()

    def marcar_en_revision(self):
        self.estado = self.ESTADO_EN_REVISION
        self.save()

    def marcar_rechazada(self):
        from django.utils import timezone
        self.estado = self.ESTADO_RECHAZADA
        self.resuelta_en = timezone.now()
        self.save()
