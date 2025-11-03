# mascota/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from .models import Mascota
from .forms import MascotaForm
from cuentas.utils import require_dueno, is_admin_like

class MascotaList(LoginRequiredMixin, ListView):
    model = Mascota
    template_name = "mascota/lista.html"
    context_object_name = "mascotas"

    def get_queryset(self):
        user = self.request.user
        # dueño ve solo sus mascotas
        if hasattr(user, "perfil") and user.perfil.rol == "DUE":
            return Mascota.objects.filter(DUENO=user).order_by("nombre")
        # admin ve todas
        if is_admin_like(user):
            return Mascota.objects.all().order_by("DUENO__username", "nombre")
        # vet aprobado puede ver todas (puede cambiarse a “solo atendidas”)
        if hasattr(user, "perfil") and user.perfil.rol == "VET":
            return Mascota.objects.all().order_by("DUENO__username", "nombre")
        # fallback
        return Mascota.objects.none()


class MascotaCreate(LoginRequiredMixin, CreateView):
    model = Mascota
    form_class = MascotaForm
    template_name = "mascota/form.html"
    success_url = reverse_lazy("mascota:lista")

    def form_valid(self, form):
        # solo dueño puede crear su mascota
        require_dueno(self.request.user)
        form.instance.DUENO = self.request.user
        return super().form_valid(form)


class MascotaUpdate(LoginRequiredMixin, UpdateView):
    model = Mascota
    form_class = MascotaForm
    template_name = "mascota/form.html"
    success_url = reverse_lazy("mascota:lista")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if is_admin_like(user):
            return obj
        if obj.DUENO != user:
            raise PermissionDenied("No puede editar esta mascota.")
        return obj


class MascotaDelete(LoginRequiredMixin, DeleteView):
    model = Mascota
    template_name = "mascota/confirm_delete.html"
    success_url = reverse_lazy("mascota:lista")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if is_admin_like(user):
            return obj
        if obj.DUENO != user:
            raise PermissionDenied("No puede eliminar esta mascota.")
        return obj


class MascotaDetail(LoginRequiredMixin, DetailView):
    model = Mascota
    template_name = "mascota/detalle.html"
    context_object_name = "mascota"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if is_admin_like(user):
            return obj
        if obj.DUENO == user:
            return obj
        # vet aprobado puede ver
        if hasattr(user, "perfil") and user.perfil.rol == "VET" and user.perfil.vet_estado == "APROBADO":
            return obj
        raise PermissionDenied("No puede ver esta mascota.")
