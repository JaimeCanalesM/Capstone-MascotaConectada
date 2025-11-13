"""
Helpers para validar permisos y roles de usuario.
Centraliza lógica de autorización para reutilizarla en views, templates, etc.
"""
from django.core.exceptions import PermissionDenied
from functools import wraps


def get_perfil_or_none(user):
    """
    Obtiene el perfil del usuario de forma segura.
    Retorna None si no existe.
    """
    return getattr(user, "perfil", None)


def is_staff_or_admin(user):
    """¿Es staff o superusuario?"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def is_approved_vet(user):
    """
    ¿Es veterinario aprobado?
    Requiere: rol="VET" y vet_estado="APROBADO"
    """
    if not user.is_authenticated:
        return False
    perfil = get_perfil_or_none(user)
    return (
        perfil 
        and perfil.rol == "VET" 
        and perfil.vet_estado == "APROBADO"
    )


def is_vet(user):
    """¿Es veterinario (independientemente de estado)?"""
    if not user.is_authenticated:
        return False
    perfil = get_perfil_or_none(user)
    return perfil and perfil.rol == "VET"


def is_owner(user, obj):
    """
    ¿Es dueño del objeto?
    Busca atributo 'dueno' o 'DUENO' en el objeto.
    """
    owner = getattr(obj, "dueno", None) or getattr(obj, "DUENO", None)
    return owner == user


def is_owner_or_staff(user, obj):
    """¿Es dueño del objeto O staff?"""
    return is_staff_or_admin(user) or is_owner(user, obj)

# DECORADORES PARA VISTAS

def require_approved_vet(view_func):
    """
    Decorador: requiere ser veterinario aprobado.
    Levanta PermissionDenied si no cumple.
    
    Uso:
        @require_approved_vet
        def mi_vista(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_approved_vet(request.user):
            raise PermissionDenied(
                "Debes ser un veterinario aprobado para acceder aquí."
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def require_staff(view_func):
    """
    Decorador: requiere ser staff o superusuario.
    
    Uso:
        @require_staff
        def mi_vista(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_staff_or_admin(request.user):
            raise PermissionDenied(
                "Acceso restringido. Requiere permisos de administrador."
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def require_authenticated(view_func):
    """
    Decorador: requiere estar autenticado.
    
    Uso:
        @require_authenticated
        def mi_vista(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Debes iniciar sesión.")
        return view_func(request, *args, **kwargs)
    return wrapper