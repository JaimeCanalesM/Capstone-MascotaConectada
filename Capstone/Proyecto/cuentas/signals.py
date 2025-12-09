from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Perfil


@receiver(pre_save, sender=Perfil)
def notificar_cambio_estado_veterinario(sender, instance, **kwargs):
    """
    Envía un correo al veterinario cuando su estado cambia de PENDIENTE a APROBADO o RECHAZADO.
    """
    # Solo procesar si el perfil ya existe (no es creación)
    if not instance.pk:
        return

    # Solo procesar si es un veterinario
    if instance.rol != Perfil.ROL_VET:
        return

    try:
        # Obtener el estado anterior
        perfil_anterior = Perfil.objects.get(pk=instance.pk)
        estado_anterior = perfil_anterior.vet_estado
        estado_nuevo = instance.vet_estado

        # Solo enviar correo si el estado cambió desde PENDIENTE
        if estado_anterior == Perfil.VET_PENDIENTE and estado_nuevo != Perfil.VET_PENDIENTE:

            usuario = instance.user

            if estado_nuevo == Perfil.VET_APROBADO:
                # Veterinario aprobado
                asunto = "¡Tu cuenta de veterinario ha sido aprobada! - MascotaConectada"
                template = "emails/veterinario_aprobado.html"
            elif estado_nuevo == Perfil.VET_RECHAZADO:
                # Veterinario rechazado
                asunto = "Actualización sobre tu solicitud de veterinario - MascotaConectada"
                template = "emails/veterinario_rechazado.html"
            else:
                return

            # Renderizar el contenido del correo
            contexto = {
                'nombre': usuario.get_full_name() or usuario.username,
                'username': usuario.username,
                'email': usuario.email,
                'vet_rut': instance.vet_rut,
                'vet_registro': instance.vet_registro,
                'vet_clinica': instance.vet_clinica,
                'observaciones': instance.vet_observaciones if estado_nuevo == Perfil.VET_RECHAZADO else None,
            }

            mensaje_html = render_to_string(template, contexto)

            # Enviar el correo
            send_mail(
                subject=asunto,
                message='',  # Mensaje en texto plano (vacío porque usamos HTML)
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                html_message=mensaje_html,
                fail_silently=False,
            )

    except Perfil.DoesNotExist:
        # El perfil no existe todavía (creación), no hacer nada
        pass
    except Exception as e:
        # Log del error pero no interrumpir el guardado
        print(f"Error enviando correo de notificación: {e}")
