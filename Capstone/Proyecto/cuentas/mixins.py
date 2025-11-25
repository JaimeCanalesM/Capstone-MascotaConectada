from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class RolRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    roles_permitidos = tuple()
    def test_func(self):
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        if not user.is_authenticated or not perfil:
            return False
        return perfil.rol in self.roles_permitidos

class SoloStaffMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        return u.is_staff or u.is_superuser

# VET o STAFF (acceso total a citas/historial)
class VetOrStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Permite acceso a veterinarios aprobados y staff/superuser"""
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False

        # Staff y superuser siempre tienen acceso
        if user.is_staff or user.is_superuser:
            return True

        # Veterinarios aprobados tienen acceso
        perfil = getattr(user, "perfil", None)
        if perfil and perfil.rol == "VET" and perfil.vet_estado == "APROBADO":
            return True

        return False

# DUENO puede ver (read-only) lo propio; VET/STAFF acceso total
class CitasReadOrVetStaffMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Para vistas de LIST/DETAIL de Citas."""
    def test_func(self):
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        return bool(user.is_authenticated)  # cualquiera autenticado puede entrar
    # El filtrado por rol/ownership se hará en get_queryset

class HistorialReadOrVetStaffMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Para vistas de LIST/DETAIL de Historial."""
    def test_func(self):
        user = self.request.user
        return bool(user.is_authenticated)

class DuenoOrVetCanEditMascotaMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    DEPRECADO: Usar NadiePuedeEditarMascotaMixin
    Dueño de la mascota, VET o STAFF pueden editar mascotas.
    """
    def test_func(self):
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        obj = self.get_object()
        if not user.is_authenticated:
            return False
        # VET o STAFF: acceso total
        if (perfil and perfil.rol == "VET") or user.is_staff or user.is_superuser:
            return True
        # DUENO: solo si es el dueño de la mascota
        return obj.DUENO_id == user.id


class NadiePuedeEditarMascotaMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    NUEVO: Nadie puede editar ni eliminar mascotas directamente.
    Los dueños deben usar el sistema de solicitudes.
    Admin y veterinarios NO tienen permisos de edición/eliminación en la interfaz de usuario.
    """
    def test_func(self):
        # NADIE puede editar/eliminar mascotas desde la interfaz
        # Deben usar el sistema de solicitudes
        return False