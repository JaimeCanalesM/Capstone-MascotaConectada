# mascota/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from .models import Mascota
from .forms import MascotaForm
from cuentas.utils import is_admin_like

class MascotaList(LoginRequiredMixin, ListView):
    model = Mascota
    template_name = "mascota/lista.html"
    context_object_name = "mascotas"

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "perfil") and user.perfil.rol == "DUENO":
            return Mascota.objects.filter(DUENO=user).order_by("nombre")
        if is_admin_like(user):
            return Mascota.objects.all().order_by("DUENO__username", "nombre")
        if hasattr(user, "perfil") and user.perfil.rol == "VET":
            return Mascota.objects.all().order_by("DUENO__username", "nombre")
        return Mascota.objects.none()


class MascotaCreate(LoginRequiredMixin, CreateView):
    model = Mascota
    form_class = MascotaForm
    template_name = "mascota/form.html"
    success_url = reverse_lazy("mascota:lista")

    def form_valid(self, form):
        if hasattr(self.request.user, "perfil") and self.request.user.perfil.rol != "DUENO":
            raise PermissionDenied("Solo los dueños pueden registrar mascotas.")
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
            raise PermissionDenied("No puedes editar esta mascota.")
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
            raise PermissionDenied("No puedes eliminar esta mascota.")
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
        if hasattr(user, "perfil") and user.perfil.rol == "VET" and user.perfil.vet_estado == "APROBADO":
            return obj
        raise PermissionDenied("No puedes ver esta mascota.")