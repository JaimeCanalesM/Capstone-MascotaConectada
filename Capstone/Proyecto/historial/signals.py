"""
Signals para sincronizar Citas con Eventos Clínicos.
Cuando una cita se marca como COMPLETADA, se crea automáticamente
un registro en el historial clínico.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

import logging

logger = logging.getLogger(__name__)


def setup_signals():
    """
    Configura manualmente los signals.
    Se llama desde historial/apps.py ready()
    """
    from citas.models import Cita
    from historial.models import EventoClinico
    
    @receiver(post_save, sender=Cita, dispatch_uid="cita_post_save_signal")
    def handle_cita_post_save(sender, instance, created, **kwargs):
        """
        Se dispara cuando se guarda una Cita.
        """
        # Si es nueva, solo registrar en logs
        if created:
            logger.info(f"Nueva Cita creada: ID={instance.id}, Mascota={instance.mascota.nombre}")
            return
        
        # Si NO es COMPLETADA, ignorar
        if instance.estado != "COMPLETADA":
            return
        
        # Verificar si ya existe evento similar
        existe = EventoClinico.objects.filter(
            mascota=instance.mascota,
            fecha=instance.fecha_hora.date(),
            tipo="CONTROL"
        ).exists()
        
        if existe:
            return
        
        # Crear el evento clínico
        try:
            evento = EventoClinico.objects.create(
                mascota=instance.mascota,
                tipo="CONTROL",
                fecha=instance.fecha_hora.date(),
                titulo=f"Cita completada: {instance.motivo}",
                descripcion=instance.notas or "Sin notas",
                veterinario=instance.veterinario
            )
            logger.info(f"EventoClinico creado: {evento.id} para Cita {instance.id}")
        except Exception as e:
            logger.error(f"Error creando EventoClinico: {e}")