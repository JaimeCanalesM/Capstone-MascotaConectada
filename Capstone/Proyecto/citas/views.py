from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView

from .forms import CitaForm
from .models import Cita


class DuenoOrVetQuerysetMixin:
    """Filtra el queryset según el rol del usuario.
    - Staff/superuser: ve todo.
    - Vet: ve citas asignadas a él.
    - Dueño: ve solo sus citas.
    """

    def get_queryset(self):
        qs = Cita.objects.all()
        u = self.request.user
        if not u.is_authenticated:
            return qs.none()
        if u.is_superuser or u.is_staff:
            return qs
        # Si el usuario tiene perfil VET, ver las asignadas
        perfil = getattr(u, "perfil", None)
        if perfil and getattr(perfil, "rol", None) == "VET":
            return qs.filter(veterinario=u)
        # Por defecto, dueños ven sus citas
        return qs.filter(dueno=u)


class CitaList(LoginRequiredMixin, DuenoOrVetQuerysetMixin, ListView):
    """Lista de citas para el usuario autenticado (dueño/vet/staff)."""
    model = Cita
    template_name = "citas/lista.html"
    context_object_name = "citas"
    paginate_by = 10


class CitaDetail(LoginRequiredMixin, DuenoOrVetQuerysetMixin, DetailView):
    """Detalle visible según el filtro del mixin."""
    model = Cita
    template_name = "citas/detalle.html"
    context_object_name = "cita"


class CitaOwnerRequiredMixin(UserPassesTestMixin):
    """Restringe edición/eliminación a:
    - Staff/superuser: permitido.
    - Dueño de la cita: permitido.
    (Vet NO edita desde aquí; si se requiere, crear flujo separado.)
    """

    def test_func(self):
        u = self.request.user
        if u.is_superuser or u.is_staff:
            return True
        obj = self.get_object()
        return obj.dueno_id == u.id

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permisos para esta acción.")
        return redirect("citas:lista")


class CitaCreate(LoginRequiredMixin, CreateView):
    """Creación de cita por el dueño. Se setea dueno = request.user en form_valid."""
    model = Cita
    form_class = CitaForm
    template_name = "citas/form.html"
    success_url = reverse_lazy("citas:lista")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Para filtrar mascotas del dueño
        return kwargs

    def form_valid(self, form):
        cita = form.save(commit=False)
        cita.dueno = self.request.user
        cita.save()
        messages.success(self.request, "Cita creada correctamente.")
        return super().form_valid(form)


class CitaUpdate(LoginRequiredMixin, CitaOwnerRequiredMixin, UpdateView):
    """Edición de cita (solo dueño y staff)."""
    model = Cita
    form_class = CitaForm
    template_name = "citas/form.html"
    success_url = reverse_lazy("citas:lista")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # mantener filtro de mascotas
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Cita actualizada.")
        return super().form_valid(form)


class CitaDelete(LoginRequiredMixin, CitaOwnerRequiredMixin, DeleteView):
    """Borrado de cita (solo dueño y staff)."""
    model = Cita
    template_name = "citas/confirm_delete.html"
    success_url = reverse_lazy("citas:lista")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Cita eliminada.")
        return super().delete(request, *args, **kwargs)
