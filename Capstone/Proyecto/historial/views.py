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
        mascota_pk = self.kwargs.get("mascota_pk")
        user = self.request.user
        perfil = getattr(user, "perfil", None)

        qs = EventoClinico.objects.select_related("mascota", "veterinario")

        # Filter by mascota first
        if mascota_pk:
            qs = qs.filter(mascota_id=mascota_pk)

        # Apply user permissions
        if perfil and perfil.rol == "VET":
            pass  # vet can see all
        elif user.is_staff or user.is_superuser:
            pass  # admin can see all
        else:
            # DUENO: eventos de sus mascotas
            qs = qs.filter(mascota__DUENO=user)

        return qs.order_by("-fecha")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        mascota_pk = self.kwargs.get("mascota_pk")
        if mascota_pk:
            ctx["mascota"] = get_object_or_404(Mascota, pk=mascota_pk)
        return ctx

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
    form_class = EventoClinicoForm
    template_name = "historial/form.html"

    def dispatch(self, request, *args, **kwargs):
        mascota_pk = self.kwargs.get("mascota_pk")
        self.mascota = get_object_or_404(Mascota, pk=mascota_pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.mascota = self.mascota
        messages.success(self.request, "Evento clínico agregado correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("historial:lista", kwargs={"mascota_pk": self.mascota.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mascota"] = self.mascota
        ctx["accion"] = "Nuevo"
        return ctx

class EventoClinicoUpdate(VetOrStaffRequiredMixin, UpdateView):
    model = EventoClinico
    form_class = EventoClinicoForm
    template_name = "historial/form.html"

    def form_valid(self, form):
        messages.success(self.request, "Evento clínico actualizado correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("historial:lista", kwargs={"mascota_pk": self.object.mascota.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mascota"] = self.object.mascota
        ctx["accion"] = "Editar"
        return ctx

class EventoClinicoDelete(VetOrStaffRequiredMixin, DeleteView):
    model = EventoClinico
    template_name = "historial/confirm_delete.html"

    def get_success_url(self):
        messages.success(self.request, "Evento clínico eliminado correctamente.")
        return reverse("historial:lista", kwargs={"mascota_pk": self.object.mascota.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mascota"] = self.object.mascota
        return ctx
