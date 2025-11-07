# panel/services.py
from django.core.mail import send_mail
from django.conf import settings

def notificar_vet(email: str, aprobado: bool, nombre_usuario: str = ""):
    asunto = "Verificación de cuenta veterinaria"
    if aprobado:
        cuerpo = (
            f"Hola {nombre_usuario or ''},\n\n"
            "¡Tu cuenta de veterinario fue aprobada!\n"
            "Ya puedes iniciar sesión y gestionar atenciones.\n\n"
            "Saludos,\nMascotaConectada"
        )
    else:
        cuerpo = (
            f"Hola {nombre_usuario or ''},\n\n"
            "Tu solicitud de cuenta veterinaria fue rechazada.\n"
            "Si crees que es un error, responde a este correo adjuntando antecedentes.\n\n"
            "Saludos,\nMascotaConectada"
        )
    send_mail(asunto, cuerpo, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
