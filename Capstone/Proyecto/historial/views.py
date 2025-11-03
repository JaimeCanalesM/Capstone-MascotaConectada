# historial/views.py
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView

from mascota.models import Mascota
from .models import EventoClinico
from .forms import EventoClinicoForm


class EventoClinicoList(LoginRequiredMixin, ListView):
    template_name = "historial/lista.html"
    context_object_name = "eventos"

    def get_queryset(self):
        mascota_id = self.kwargs["mascota_id"]
        return EventoClinico.objects.filter(mascota_id=mascota_id).order_by("-fecha")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        mascota_id = self.kwargs["mascota_id"]
        ctx["mascota"] = get_object_or_404(Mascota, pk=mascota_id)
        return ctx


class EventoClinicoCreate(LoginRequiredMixin, CreateView):
    model = EventoClinico
    form_class = EventoClinicoForm
    template_name = "historial/form.html"

    def form_valid(self, form):
        mascota_id = self.kwargs["mascota_id"]
        mascota = get_object_or_404(Mascota, pk=mascota_id)
        obj = form.save(commit=False)
        obj.mascota = mascota
        # si el que crea es vet aprobado, se guarda
        if hasattr(self.request.user, "perfil"):
            p = self.request.user.perfil
            if p and p.rol == "VET" and p.vet_estado == "APROBADO":
                obj.veterinario = self.request.user
        obj.save()
        messages.success(self.request, "Evento clínico creado.")
        return redirect("historial:lista", mascota_id=mascota_id)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mascota"] = get_object_or_404(Mascota, pk=self.kwargs["mascota_id"])
        return ctx


class EventoClinicoDetail(LoginRequiredMixin, TemplateView):
    template_name = "historial/detalle.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        mascota_id = self.kwargs["mascota_id"]
        evento_id = self.kwargs["evento_id"]
        ctx["mascota"] = get_object_or_404(Mascota, pk=mascota_id)
        ctx["evento"] = get_object_or_404(EventoClinico, pk=evento_id, mascota_id=mascota_id)
        return ctx


class EventoClinicoUpdate(LoginRequiredMixin, UpdateView):
    model = EventoClinico
    form_class = EventoClinicoForm
    template_name = "historial/form.html"

    def get_object(self, queryset=None):
        mascota_id = self.kwargs["mascota_id"]
        evento_id = self.kwargs["evento_id"]
        return get_object_or_404(EventoClinico, pk=evento_id, mascota_id=mascota_id)

    def form_valid(self, form):
        obj = form.save()
        messages.success(self.request, "Evento clínico actualizado.")
        return redirect("historial:detalle", mascota_id=obj.mascota_id, evento_id=obj.id)


class EventoClinicoDelete(LoginRequiredMixin, DeleteView):
    template_name = "historial/confirm_delete.html"

    def get_object(self, queryset=None):
        mascota_id = self.kwargs["mascota_id"]
        evento_id = self.kwargs["evento_id"]
        return get_object_or_404(EventoClinico, pk=evento_id, mascota_id=mascota_id)

    def get_success_url(self):
        messages.success(self.request, "Evento clínico eliminado.")
        return reverse_lazy("historial:lista", kwargs={"mascota_id": self.kwargs["mascota_id"]})
