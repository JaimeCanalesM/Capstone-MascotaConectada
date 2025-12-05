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
    """
    Lista de citas filtradas por rol del usuario.
    Usa el QuerySet personalizado para simplificar lógica.
    """
    model = Cita
    template_name = "citas/lista.html"
    context_object_name = "todas"
    paginate_by = 20

    def get_queryset(self):
        """
        Retorna citas del usuario con búsqueda opcional.
        Usa el QuerySet personalizado: .for_user() y .with_related()
        """
        # QuerySet base filtrado por rol y optimizado
        qs = (Cita.objects
              .with_related()  # Evita N+1 queries
              .for_user(self.request.user))  # Filtra por rol
        
        # Búsqueda por término (opcional)
        q = self.request.GET.get("q", "").strip()
        if q:
            filtros = (Q(motivo__icontains=q) | 
                      Q(mascota__nombre__icontains=q))
            
            # Búsqueda por dueño solo si eres staff o vet
            if self.request.user.is_staff or self._es_vet():
                filtros |= Q(dueno__username__icontains=q)
            
            qs = qs.filter(filtros)
        
        return qs.order_by("fecha_hora")
    
    def _es_vet(self):
        """Helper: ¿es veterinario?"""
        perfil = getattr(self.request.user, "perfil", None)
        return perfil and perfil.rol == "VET"

    def get_context_data(self, **kwargs):
        """
        Agrega próximas y pasadas al contexto.
        IMPORTANTE: hacemos esto ANTES de paginar en get_queryset
        """
        ctx = super().get_context_data(**kwargs)
        
        # Obtener el queryset COMPLETO (sin slice de paginación)
        # usando directamente los métodos del QuerySet
        qs_all = (Cita.objects
                  .with_related()
                  .for_user(self.request.user))
        
        # Aplicar búsqueda si existe
        q = self.request.GET.get("q", "").strip()
        if q:
            filtros = (Q(motivo__icontains=q) | 
                      Q(mascota__nombre__icontains=q))
            
            if self.request.user.is_staff or self._es_vet():
                filtros |= Q(dueno__username__icontains=q)
            
            qs_all = qs_all.filter(filtros)
        
        # Ahora SÍ separar próximas y pasadas (antes del slice de página)
        ctx["proximas"] = list(qs_all.proximas())
        ctx["pasadas"] = list(qs_all.pasadas())
        
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

    def dispatch(self, request, *args, **kwargs):
        # Solo administradores pueden editar citas
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "No tienes permisos para editar citas.")
            return redirect("citas:lista")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        # Administradores pueden editar cualquier cita
        return super().get_queryset()


class CitaDelete(LoginRequiredMixin, DeleteView):
    model = Cita
    template_name = "citas/confirm_delete.html"
    success_url = reverse_lazy("citas:lista")

    def dispatch(self, request, *args, **kwargs):
        # Solo administradores pueden eliminar citas
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "No tienes permisos para eliminar citas.")
            return redirect("citas:lista")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Administradores pueden eliminar cualquier cita
        return super().get_queryset()


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