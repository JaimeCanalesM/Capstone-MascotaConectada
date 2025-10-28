# citas/views.py
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, View

from .forms import CitaForm
from .models import Cita

"""
Vistas de agenda (citas):
- Lista/detalle/crear/editar/eliminar para dueños (y staff).
- "Mis atenciones" para veterinarios (citas asignadas a él).
- Acciones rápidas para cambiar estado (vet y staff).
"""

class DuenoOrVetQuerysetMixin:
    """
    Filtra el queryset según el rol del usuario:
    - staff/superuser: ve todo
    - vet: ve citas asignadas a él
    - dueños: ven solo sus citas
    """
    def get_queryset(self):
        qs = Cita.objects.select_related("mascota", "dueno", "veterinario")
        u = self.request.user
        if not u.is_authenticated:
            return qs.none()
        if u.is_superuser or u.is_staff:
            return qs
        perfil = getattr(u, "perfil", None)
        if perfil and getattr(perfil, "rol", None) == "VET":
            return qs.filter(veterinario=u)
        return qs.filter(dueno=u)


class CitaList(LoginRequiredMixin, DuenoOrVetQuerysetMixin, ListView):
    model = Cita
    template_name = "citas/lista.html"
    context_object_name = "citas"
    paginate_by = 10


class CitaDetail(LoginRequiredMixin, DuenoOrVetQuerysetMixin, DetailView):
    model = Cita
    template_name = "citas/detalle.html"
    context_object_name = "cita"


class CitaOwnerRequiredMixin(UserPassesTestMixin):
    """
    Restringe edición/eliminación a dueño o staff.
    (Vet no edita desde aquí para simplificar; si se requiere, habilitar transición separada).
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
    model = Cita
    form_class = CitaForm
    template_name = "citas/form.html"
    success_url = reverse_lazy("citas:lista")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Cita actualizada.")
        return super().form_valid(form)


class CitaDelete(LoginRequiredMixin, CitaOwnerRequiredMixin, DeleteView):
    model = Cita
    template_name = "citas/confirm_delete.html"
    success_url = reverse_lazy("citas:lista")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Cita eliminada.")
        return super().delete(request, *args, **kwargs)


# ---------- Vistas para VETERINARIO ----------

class VetOnlyMixin(UserPassesTestMixin):
    """Permite el acceso solo a usuario con perfil VET aprobado o staff/superuser."""
    def test_func(self):
        u = self.request.user
        if not u.is_authenticated:
            return False
        if u.is_superuser or u.is_staff:
            return True
        p = getattr(u, "perfil", None)
        return bool(p and p.rol == "VET" and getattr(p, "vet_estado", "") == "APROBADO")

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permisos para esta sección.")
        return redirect("citas:lista")


class CitasAsignadasList(LoginRequiredMixin, VetOnlyMixin, ListView):
    """Lista de citas asignadas al veterinario autenticado (o staff ve todas)."""
    model = Cita
    template_name = "citas/mis_atenciones.html"
    context_object_name = "citas"
    paginate_by = 10

    def get_queryset(self):
        qs = Cita.objects.select_related("mascota", "dueno", "veterinario")
        u = self.request.user
        if u.is_superuser or u.is_staff:
            return qs.order_by("-fecha_hora")
        return qs.filter(veterinario=u).order_by("-fecha_hora")


class CitaCambiarEstadoView(LoginRequiredMixin, VetOnlyMixin, View):
    """
    Cambia el estado de una cita (CONFIRMAR, COMPLETAR, CANCELAR) por parte del veterinario o staff.
    Restricciones simples:
    - Solo sobre citas asignadas al propio veterinario (salvo staff).
    - Estados válidos: CONFIRMADA, COMPLETADA, CANCELADA.
    """
    def post(self, request, pk):
        cita = get_object_or_404(Cita, pk=pk)
        u = request.user

        # Si no es staff/superuser, debe ser el vet asignado
        if not (u.is_superuser or u.is_staff):
            if cita.veterinario_id != u.id:
                messages.error(request, "La cita no está asignada a usted.")
                return redirect("citas:mis_atenciones")

        nuevo = request.POST.get("estado")
        if nuevo not in ("CONFIRMADA", "COMPLETADA", "CANCELADA"):
            messages.error(request, "Estado inválido.")
            return redirect("citas:mis_atenciones")

        cita.estado = nuevo
        cita.save(update_fields=["estado"])
        messages.success(request, f"Estado actualizado a {nuevo.title()}.")
        return redirect("citas:mis_atenciones")