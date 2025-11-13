from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView

from cuentas.mixins import HistorialReadOrVetStaffMixin, VetOrStaffRequiredMixin
from mascota.models import Mascota
from .models import EventoClinico
from .forms import EventoClinicoForm


class EventoClinicoList(HistorialReadOrVetStaffMixin, ListView):
    model = EventoClinico
    template_name = "historial/lista.html"
    context_object_name = "eventos"
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        qs = EventoClinico.objects.select_related("mascota", "veterinario")
        if perfil and perfil.rol == "VET":
            return qs  # ver todo (o filtra por veterinario si quieres)
        elif user.is_staff or user.is_superuser:
            return qs
        else:
            # DUENO: eventos de sus mascotas
            return qs.filter(mascota__DUENO=user).order_by("-fecha")

class EventoClinicoDetail(HistorialReadOrVetStaffMixin, DetailView):
    model = EventoClinico
    template_name = "historial/detalle.html"
    context_object_name = "evento"

    def get_queryset(self):
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        qs = EventoClinico.objects.select_related("mascota", "veterinario")
        if perfil and perfil.rol == "VET":
            return qs
        elif user.is_staff or user.is_superuser:
            return qs
        else:
            # DUENO: eventos de sus mascotas - USAR DUENO EN MAYÚSCULAS
            return qs.filter(mascota__DUENO=user)

class EventoClinicoCreate(VetOrStaffRequiredMixin, CreateView):
    model = EventoClinico
    form_class = EventoClinicoForm  # ← USAR form_class (no fields)
    template_name = "historial/form.html"
    success_url = reverse_lazy("historial:lista")

class EventoClinicoUpdate(VetOrStaffRequiredMixin, UpdateView):
    model = EventoClinico
    form_class = EventoClinicoForm  # ← USAR form_class (no fields)
    template_name = "historial/form.html"
    success_url = reverse_lazy("historial:lista")

class EventoClinicoDelete(VetOrStaffRequiredMixin, DeleteView):
    model = EventoClinico
    template_name = "historial/confirm_delete.html"
    success_url = reverse_lazy("historial:lista")