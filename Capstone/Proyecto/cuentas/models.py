from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Perfil(models.Model):
    ROL_DUENO = "DUENO"
    ROL_VET = "VET"
    ROLES = [
        (ROL_DUENO, "Dueño de mascota"),
        (ROL_VET, "Veterinario"),
    ]

    VET_PENDIENTE = "PENDIENTE"
    VET_APROBADO = "APROBADO"
    VET_RECHAZADO = "RECHAZADO"
    VET_ESTADOS = [
        (VET_PENDIENTE, "Pendiente"),
        (VET_APROBADO, "Aprobado"),
        (VET_RECHAZADO, "Rechazado"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    rol = models.CharField(max_length=10, choices=ROLES, default=ROL_DUENO)

    # SOLO si rol = VET:
    vet_estado = models.CharField(max_length=10, choices=VET_ESTADOS, blank=True, null=True)
    vet_registro = models.CharField(
        max_length=100, blank=True,
        help_text="Número de registro profesional (SEREMI/colegiatura, etc.)"
    )
    vet_clinica = models.CharField(max_length=200, blank=True, help_text="Clínica/centro donde ejerces")
    vet_observaciones = models.TextField(blank=True, help_text="Notas internas (solo admin)")

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        base = f"{self.user.username} ({self.get_rol_display()})"
        if self.rol == self.ROL_VET and self.vet_estado:
            return f"{base} - {self.vet_estado}"
        return base

@receiver(post_save, sender=User)
def crear_perfil_si_no_existe(sender, instance, created, **kwargs):
    if created and not hasattr(instance, "perfil"):
        Perfil.objects.create(user=instance, rol=Perfil.ROL_DUENO)
