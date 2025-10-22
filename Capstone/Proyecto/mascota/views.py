from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Mascota
from .forms import MascotaForm

class DuenoRequiredMixin(UserPassesTestMixin):
    """
    Restringe acceso a usuarios con perfil de DUEÑO.
    """
    def test_func(self):
        p = getattr(self.request.user, "perfil", None)
        return bool(self.request.user.is_authenticated and p and p.rol == "DUENO")

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permisos para esta sección.")
        from django.shortcuts import redirect
        return redirect("login")

class DueñoQuerysetMixin:
    """
    Filtra queryset a las mascotas del usuario.
    """
    def get_queryset(self):
        return Mascota.objects.filter(DUENO=self.request.user)

class MascotaList(LoginRequiredMixin, DuenoRequiredMixin, DueñoQuerysetMixin, ListView):
    template_name = "mascota/lista.html"
    context_object_name = "mascotas"

class MascotaCreate(LoginRequiredMixin, DuenoRequiredMixin, CreateView):
    model = Mascota
    form_class = MascotaForm
    template_name = "mascota/form.html"
    success_url = reverse_lazy("mascota:lista")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.DUENO = self.request.user
        obj.save()
        messages.success(self.request, "Mascota registrada correctamente 🐾")
        return super().form_valid(form)

class MascotaUpdate(LoginRequiredMixin, DuenoRequiredMixin, DueñoQuerysetMixin, UpdateView):
    model = Mascota
    form_class = MascotaForm
    template_name = "mascota/form.html"
    success_url = reverse_lazy("mascota:lista")

    def get_queryset(self):
        return super().get_queryset()  # ya filtrado

    def form_valid(self, form):
        messages.success(self.request, "Mascota actualizada.")
        return super().form_valid(form)

class MascotaDelete(LoginRequiredMixin, DuenoRequiredMixin, DueñoQuerysetMixin, DeleteView):
    model = Mascota
    template_name = "mascota/confirm_delete.html"
    success_url = reverse_lazy("mascota:lista")

    def get_queryset(self):
        return super().get_queryset()  # ya filtrado

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Mascota eliminada.")
        return super().delete(request, *args, **kwargs)

class MascotaDetail(LoginRequiredMixin, DuenoRequiredMixin, DueñoQuerysetMixin, DetailView):
    model = Mascota
    template_name = "mascota/detalle.html"
    context_object_name = "mascota"
