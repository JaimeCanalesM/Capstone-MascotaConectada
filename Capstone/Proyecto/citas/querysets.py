"""
QuerySet personalizado para Cita
Centraliza lógica de filtrado por rol de usuario
"""
from django.db import models
from django.utils import timezone


class CitaQuerySet(models.QuerySet):
    """QuerySet personalizado para Cita con lógica de filtrado por rol"""
    
    def for_user(self, user):
        """
        Filtra citas según el rol del usuario autenticado.
        
        - Staff/Superuser: ven todas las citas
        - Veterinario aprobado: ven solo sus citas asignadas
        - Dueño: ve solo sus propias citas
        """
        from cuentas.models import Perfil
        
        # Staff y superuser ven todo
        if user.is_staff or user.is_superuser:
            return self
        
        # Veterinario aprobado ve solo sus citas asignadas
        perfil = getattr(user, "perfil", None)
        if perfil and perfil.rol == "VET" and perfil.vet_estado == "APROBADO":
            return self.filter(veterinario=user)
        
        # Dueño ve solo sus citas
        return self.filter(dueno=user)
    
    def with_related(self):
        """
        Optimiza queries con select_related para evitar N+1 queries.
        Siempre usar cuando vayas a acceder a relaciones.
        """
        return self.select_related(
            "dueno",
            "mascota",
            "veterinario",
            "clinica"
        )
    
    def proximas(self):
        """
        Retorna citas futuras ordenadas por fecha.
        Útil para el listado de "próximas citas".
        """
        return self.filter(
            fecha_hora__gte=timezone.now()
        ).order_by("fecha_hora")
    
    def pasadas(self):
        """
        Retorna citas pasadas ordenadas por fecha descendente.
        Útil para el historial.
        """
        return self.filter(
            fecha_hora__lt=timezone.now()
        ).order_by("-fecha_hora")
    
    def por_estado(self, estado):
        """
        Filtra citas por estado específico.
        Estados válidos: PENDIENTE, CONFIRMADA, COMPLETADA, CANCELADA
        """
        return self.filter(estado=estado)
    
    def sin_veterinario(self):
        """Retorna citas que aún no tienen veterinario asignado"""
        return self.filter(veterinario__isnull=True)