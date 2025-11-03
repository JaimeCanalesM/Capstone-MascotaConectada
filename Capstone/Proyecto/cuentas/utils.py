# cuentas/utils.py
from django.core.exceptions import PermissionDenied

def require_dueno(user):
    """
    Permite solo usuarios autenticados con perfil de DUEÑO.
    """
    if not user.is_authenticated:
        raise PermissionDenied("Usuario no autenticado.")
    if not hasattr(user, "perfil"):
        raise PermissionDenied("El usuario no tiene perfil.")
    if user.perfil.rol != "DUE":
        raise PermissionDenied("Se requiere rol de dueño.")

def require_vet_aprobado(user):
    """
    Permite solo veterinarios con estado APROBADO.
    """
    if not user.is_authenticated:
        raise PermissionDenied("Usuario no autenticado.")
    if not hasattr(user, "perfil"):
        raise PermissionDenied("El usuario no tiene perfil.")
    if user.perfil.rol != "VET":
        raise PermissionDenied("Se requiere rol de veterinario.")
    if user.perfil.vet_estado != "APROBADO":
        raise PermissionDenied("El veterinario no está aprobado.")

def is_admin_like(user):
    """
    Devuelve True si es staff o superusuario.
    """
    return user.is_authenticated and (user.is_staff or user.is_superuser)
