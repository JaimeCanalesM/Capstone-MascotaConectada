from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):

    # --- ROLES ---
    ROL_DUENO = "DUENO"
    ROL_VET = "VET"

    ROLES = [
        (ROL_DUENO, "Dueño de mascota"),
        (ROL_VET, "Veterinario"),
    ]

    # --- ESTADOS DE VETERINARIO ---
    VET_PENDIENTE = "PENDIENTE"
    VET_APROBADO = "APROBADO"
    VET_RECHAZADO = "RECHAZADO"

    VET_ESTADOS = [
        (VET_PENDIENTE, "Pendiente"),
        (VET_APROBADO, "Aprobado"),
        (VET_RECHAZADO, "Rechazado"),
    ]

    # --- RELACIÓN ---
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil"
    )

    # --- DATOS DEL PERFIL ---
    rol = models.CharField(
        max_length=10,
        choices=ROLES,
        default=ROL_DUENO
    )

    # --- CAMPOS EXCLUSIVOS PARA VETERINARIOS ---
    vet_estado = models.CharField(
        max_length=10,
        choices=VET_ESTADOS,
        default=VET_PENDIENTE,
        blank=True,
        null=True
    )

    vet_registro = models.CharField(
        max_length=100,
        blank=True,
        help_text="Número de registro profesional (SEREMI/colegiatura, etc.)"
    )

    vet_clinica = models.CharField(
        max_length=200,
        blank=True,
        help_text="Clínica o centro donde ejerce"
    )

    licencia_medica = models.FileField(
        upload_to="licencias_vets/",
        blank=True,
        null=True,
        help_text="Documento obligatorio para veterinarios (PDF/JPG/PNG)"
    )

    vet_observaciones = models.TextField(
        blank=True,
        help_text="Notas internas visibles solo para el administrador"
    )

    # --- TIMESTAMPS ---
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    # --- REPRESENTACIÓN ---
    def __str__(self):
        base = f"{self.user.username} ({self.get_rol_display()})"
        if self.rol == self.ROL_VET and self.vet_estado:
            return f"{base} - {self.vet_estado}"
        return base

    # --- VALIDACIÓN INTERNA ---
    def save(self, *args, **kwargs):
        if self.rol == self.ROL_VET:
            # Siempre debe tener estado
            if not self.vet_estado:
                self.vet_estado = self.VET_PENDIENTE
        super().save(*args, **kwargs)


# --- SIGNAL: CREAR PERFIL AUTOMÁTICAMENTE ---
@receiver(post_save, sender=User)
def crear_perfil_si_no_existe(sender, instance, created, **kwargs):
    if created:
        # Todos los usuarios nuevos parten con rol dueño
        Perfil.objects.create(user=instance, rol=Perfil.ROL_DUENO)
