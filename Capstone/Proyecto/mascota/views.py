from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, DeleteView, DetailView, CreateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import redirect
from cuentas.mixins import DuenoOrVetCanEditMascotaMixin, NadiePuedeEditarMascotaMixin, VetOrStaffRequiredMixin
from .models import Mascota
from .forms import MascotaForm

class MascotaList(LoginRequiredMixin, ListView):
    model = Mascota
    template_name = "mascota/lista.html"
    context_object_name = "mascotas"
    paginate_by = 12

    def get_queryset(self):
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        qs = Mascota.objects.select_related("DUENO").all()

        # DUENO: solo sus mascotas
        if not (perfil and perfil.rol == "VET") and not user.is_staff and not user.is_superuser:
            qs = qs.filter(DUENO=user)

        # Filtros adicionales para admin/vet
        especie = self.request.GET.get("especie")
        if especie:
            qs = qs.filter(especie__icontains=especie)

        raza = self.request.GET.get("raza")
        if raza:
            qs = qs.filter(raza__icontains=raza)

        sexo = self.request.GET.get("sexo")
        if sexo:
            qs = qs.filter(sexo=sexo)

        # Búsqueda general
        q = self.request.GET.get("q")
        if q:
            filtros = Q(nombre__icontains=q) | Q(raza__icontains=q) | Q(especie__icontains=q)
            if (perfil and perfil.rol == "VET") or user.is_staff or user.is_superuser:
                filtros |= Q(DUENO__username__icontains=q) | Q(DUENO__email__icontains=q)
            qs = qs.filter(filtros)

        return qs.order_by("nombre")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        perfil = getattr(user, "perfil", None)

        # Indicar si el usuario es admin o vet
        ctx["es_admin_o_vet"] = (perfil and perfil.rol == "VET") or user.is_staff or user.is_superuser

        # Valores actuales de los filtros
        ctx["especie_actual"] = self.request.GET.get("especie", "")
        ctx["raza_actual"] = self.request.GET.get("raza", "")
        ctx["sexo_actual"] = self.request.GET.get("sexo", "")
        ctx["q"] = self.request.GET.get("q", "")

        # Opciones de especies y razas para los filtros
        if ctx["es_admin_o_vet"]:
            ctx["especies_disponibles"] = Mascota.objects.values_list('especie', flat=True).distinct().order_by('especie')
            ctx["razas_disponibles"] = Mascota.objects.values_list('raza', flat=True).distinct().order_by('raza')

        return ctx
    
class MascotaDetail(LoginRequiredMixin, DetailView):
    model = Mascota
    template_name = "mascota/detalle.html"
    context_object_name = "mascota"

    def get_queryset(self):
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        qs = Mascota.objects.select_related("DUENO")
        if (perfil and perfil.rol == "VET") or user.is_staff or user.is_superuser:
            return qs
        return qs.filter(DUENO=user)
    
class MascotaCreate(LoginRequiredMixin, CreateView):
    model = Mascota
    form_class = MascotaForm  # Usar el formulario
    template_name = "mascota/form.html"
    success_url = reverse_lazy("mascota:lista")

    def form_valid(self, form):
        # La mascota siempre pertenece al usuario autenticado
        form.instance.DUENO = self.request.user
        return super().form_valid(form)

class MascotaUpdate(NadiePuedeEditarMascotaMixin, UpdateView):
    """
    Vista de edición de mascotas - BLOQUEADA.
    Los dueños deben usar el sistema de solicitudes para editar mascotas.
    Admin y veterinarios tampoco pueden editar desde aquí (solo desde Django admin si es necesario).
    """
    model = Mascota
    form_class = MascotaForm
    template_name = "mascota/form.html"
    success_url = reverse_lazy("mascota:lista")

    def get(self, request, *args, **kwargs):
        messages.error(
            request,
            "No puedes editar mascotas directamente. "
            "Envía una solicitud al administrador desde el menú 'Solicitudes'."
        )
        return redirect('mascota:lista')


class MascotaDelete(NadiePuedeEditarMascotaMixin, DeleteView):
    """
    Vista de eliminación de mascotas - BLOQUEADA.
    Los dueños deben usar el sistema de solicitudes para eliminar mascotas.
    """
    model = Mascota
    template_name = "mascota/confirm_delete.html"
    success_url = reverse_lazy("mascota:lista")

    def get(self, request, *args, **kwargs):
        messages.error(
            request,
            "No puedes eliminar mascotas directamente. "
            "Envía una solicitud al administrador desde el menú 'Solicitudes'."
        )
        return redirect('mascota:lista')


class MascotaUpdateVet(VetOrStaffRequiredMixin, UpdateView):
    """
    Vista especial para que veterinarios y admin puedan editar campos específicos:
    - peso (kg)
    - sexo
    - notas
    """
    model = Mascota
    fields = ['peso', 'sexo', 'notas']
    template_name = "mascota/form_vet.html"

    def get_queryset(self):
        # Veterinarios y admin pueden editar cualquier mascota
        return Mascota.objects.select_related("DUENO").all()

    def get_success_url(self):
        return reverse_lazy("mascota:detalle", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Información médica de {form.instance.nombre} actualizada correctamente."
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['accion'] = 'Actualizar Información Médica'
        ctx['mascota'] = self.object
        return ctx