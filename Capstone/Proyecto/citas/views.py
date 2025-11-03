# citas/views.py
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .models import Cita
from .forms import CitaForm
from historial.models import EventoClinico


# valores de estado usados en el modelo Cita (mantener igual que en models.py)
ESTADO_PENDIENTE = "PENDIENTE"
ESTADO_ATENDIDA = "ATENDIDA"
ESTADO_CANCELADA = "CANCELADA"


class CitaList(LoginRequiredMixin, ListView):
    model = Cita
    template_name = "citas/lista.html"
    context_object_name = "citas"

    def get_queryset(self):
        user = self.request.user
        qs = Cita.objects.select_related("mascota", "dueno", "clinica", "veterinario")

        # dueño ve solo las suyas
        if hasattr(user, "perfil") and user.perfil and user.perfil.rol == "DUE":
            qs = qs.filter(dueno=user)
        # vet ve solo las asignadas
        elif hasattr(user, "perfil") and user.perfil and user.perfil.rol == "VET":
            qs = qs.filter(veterinario=user)
        # admin ve todas

        return qs.order_by("-fecha_hora")


class ProximasCitas(LoginRequiredMixin, ListView):
    model = Cita
    template_name = "citas/proximas.html"
    context_object_name = "citas"

    def get_queryset(self):
        ahora = datetime.now()
        limite = ahora + timedelta(days=7)
        user = self.request.user
        qs = Cita.objects.filter(fecha_hora__gte=ahora, fecha_hora__lte=limite)

        if hasattr(user, "perfil") and user.perfil and user.perfil.rol == "DUE":
            qs = qs.filter(dueno=user)
        elif hasattr(user, "perfil") and user.perfil and user.perfil.rol == "VET":
            qs = qs.filter(veterinario=user)

        return qs.order_by("fecha_hora")


class CitaCreate(LoginRequiredMixin, CreateView):
    model = Cita
    form_class = CitaForm
    template_name = "citas/form.html"
    success_url = reverse_lazy("citas:lista")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # el form puede filtrar mascotas por usuario
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        cita = form.save(commit=False)
        cita.dueno = self.request.user
        # por defecto pendiente
        if not cita.estado:
            cita.estado = ESTADO_PENDIENTE
        cita.save()
        messages.success(self.request, "Cita creada correctamente.")
        return super().form_valid(form)


class CitaUpdate(LoginRequiredMixin, UpdateView):
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


class CitaDelete(LoginRequiredMixin, DeleteView):
    model = Cita
    template_name = "citas/confirm_delete.html"
    success_url = reverse_lazy("citas:lista")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Cita eliminada.")
        return super().delete(request, *args, **kwargs)


class CitaCompletar(LoginRequiredMixin, View):
    def post(self, request, pk):
        cita = get_object_or_404(Cita, pk=pk)

        # control de permisos
        u = request.user
        puede = False
        if u.is_staff or u.is_superuser:
            puede = True
        elif hasattr(u, "perfil") and u.perfil and u.perfil.rol == "VET" and u.perfil.vet_estado == "APROBADO":
            puede = True

        if not puede:
            messages.error(request, "No tiene permisos para completar esta cita.")
            return redirect("citas:lista")

        cita.estado = ESTADO_ATENDIDA
        cita.save()
        messages.success(request, "Cita marcada como atendida.")
        return redirect("citas:lista")


class CitaToHistorial(LoginRequiredMixin, View):
    """
    Convierte una cita ATENDIDA en un evento clínico.
    """

    def post(self, request, pk):
        cita = get_object_or_404(Cita, pk=pk)

        # permisos
        u = request.user
        puede = False
        if u.is_staff or u.is_superuser:
            puede = True
        elif hasattr(u, "perfil") and u.perfil and u.perfil.rol == "VET" and u.perfil.vet_estado == "APROBADO":
            puede = True

        if not puede:
            messages.error(request, "No tiene permisos para enviar esta cita al historial.")
            return redirect("citas:lista")

        if not cita.mascota:
            messages.error(request, "La cita no tiene mascota asociada.")
            return redirect("citas:lista")

        # crear evento
        EventoClinico.objects.create(
            mascota=cita.mascota,
            fecha=cita.fecha_hora.date() if cita.fecha_hora else datetime.now().date(),
            tipo="CONSULTA",
            veterinario=cita.veterinario,
            descripcion=f"Atención generada desde la cita #{cita.id}. Motivo: {cita.motivo or '—'}",
        )

        # asegurar que la cita queda atendida
        cita.estado = ESTADO_ATENDIDA
        cita.save()

        messages.success(request, "Se creó el evento en el historial de la mascota.")
        return redirect("historial:lista", mascota_id=cita.mascota.id)


class MisAtenciones(LoginRequiredMixin, ListView):
    model = Cita
    template_name = "citas/mis_atenciones.html"
    context_object_name = "citas"

    def get_queryset(self):
        u = self.request.user
        qs = Cita.objects.filter(estado=ESTADO_ATENDIDA)
        if u.is_staff or u.is_superuser:
            return qs.order_by("-fecha_hora")
        if hasattr(u, "perfil") and u.perfil and u.perfil.rol == "VET":
            return qs.filter(veterinario=u).order_by("-fecha_hora")
        return qs.none()
