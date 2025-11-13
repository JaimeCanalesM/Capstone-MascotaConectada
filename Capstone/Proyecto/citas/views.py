from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from cuentas.mixins import CitasReadOrVetStaffMixin, VetOrStaffRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)

from citas.models import Cita
from .forms import CitaForm
from historial.models import EventoClinico


# Valores de estado
ESTADO_PENDIENTE = "PENDIENTE"
ESTADO_COMPLETADA = "COMPLETADA"
ESTADO_CANCELADA = "CANCELADA"


class CitaList(CitasReadOrVetStaffMixin, ListView):
    model = Cita
    template_name = "citas/lista.html"
    context_object_name = "todas"
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        qs = Cita.objects.select_related("dueno", "mascota", "veterinario", "clinica")
        
        if perfil and perfil.rol == "VET":
            qs = qs.filter(veterinario=user)
        elif user.is_staff or user.is_superuser:
            pass
        else:
            qs = qs.filter(dueno=user)

        q = self.request.GET.get("q")
        if q:
            filtros = Q(motivo__icontains=q) | Q(mascota__nombre__icontains=q) | Q(dueno__username__icontains=q)
            if perfil and (perfil.rol == "VET" or user.is_staff or user.is_superuser):
                filtros |= Q(clinica__nombre__icontains=q)
            qs = qs.filter(filtros)
        
        return qs.order_by("fecha_hora")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ahora = timezone.now()
        qs = ctx["todas"]
        ctx["proximas"] = [c for c in qs if c.fecha_hora >= ahora]
        ctx["pasadas"] = [c for c in qs if c.fecha_hora < ahora]
        
        perfil = getattr(self.request.user, "perfil", None)
        ctx["puede_gestionar"] = bool(
            (perfil and perfil.rol == "VET") or self.request.user.is_staff or self.request.user.is_superuser
        )
        return ctx


class CitaDetail(CitasReadOrVetStaffMixin, DetailView):
    model = Cita
    template_name = "citas/detalle.html"
    context_object_name = "cita"

    def get_queryset(self):
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        qs = Cita.objects.select_related("dueno", "mascota", "veterinario", "clinica")
        
        if perfil and perfil.rol == "VET":
            return qs.filter(veterinario=user)
        elif user.is_staff or user.is_superuser:
            return qs
        else:
            return qs.filter(dueno=user)


class CitaCreate(LoginRequiredMixin, CreateView):
    model = Cita
    form_class = CitaForm
    template_name = "citas/form.html"
    success_url = reverse_lazy("citas:lista")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.dueno = self.request.user
        return super().form_valid(form)


class CitaUpdate(LoginRequiredMixin, UpdateView):
    model = Cita
    form_class = CitaForm
    template_name = "citas/form.html"
    success_url = reverse_lazy("citas:lista")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        qs = super().get_queryset()
        
        if perfil and perfil.rol == "VET":
            return qs.filter(veterinario=user)
        elif not (user.is_staff or user.is_superuser):
            return qs.filter(dueno=user)
        return qs


class CitaDelete(LoginRequiredMixin, DeleteView):
    model = Cita
    template_name = "citas/confirm_delete.html"
    success_url = reverse_lazy("citas:lista")

    def get_queryset(self):
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        qs = super().get_queryset()
        
        if perfil and perfil.rol == "VET":
            return qs.filter(veterinario=user)
        elif not (user.is_staff or user.is_superuser):
            return qs.filter(dueno=user)
        return qs


class CitaCompletar(LoginRequiredMixin, View):
    def post(self, request, pk):
        cita = get_object_or_404(Cita, pk=pk)

        u = request.user
        puede = False
        if u.is_staff or u.is_superuser:
            puede = True
        elif hasattr(u, "perfil") and u.perfil and u.perfil.rol == "VET" and u.perfil.vet_estado == "APROBADO":
            puede = True

        if not puede:
            messages.error(request, "No tiene permisos para completar esta cita.")
            return redirect("citas:lista")

        cita.estado = ESTADO_COMPLETADA
        cita.save()
        messages.success(request, "Cita marcada como completada.")
        return redirect("citas:lista")


class CitasAtendidasView(LoginRequiredMixin, ListView):
    model = Cita
    template_name = "citas/mis_atenciones.html"
    context_object_name = "citas"
    paginate_by = 20

    def get_queryset(self):
        qs = Cita.objects.select_related("dueno", "mascota", "veterinario", "clinica").filter(estado="COMPLETADA")
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        
        if perfil and perfil.rol == "VET" and not (user.is_staff or user.is_superuser):
            qs = qs.filter(veterinario=user)
        
        return qs.order_by("-fecha_hora")