from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, DeleteView, DetailView, CreateView
from django.urls import reverse_lazy
from django.db.models import Q
from cuentas.mixins import DuenoOrVetCanEditMascotaMixin
from .models import Mascota
from .forms import MascotaForm

class MascotaList(LoginRequiredMixin, ListView):
    model = Mascota
    template_name = "mascota/lista.html"
    context_object_name = "mascotas"
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        qs = Mascota.objects.select_related("DUENO").all()

        # DUENO: solo sus mascotas
        if not (perfil and perfil.rol == "VET") and not user.is_staff and not user.is_superuser:
            qs = qs.filter(DUENO=user)

        q = self.request.GET.get("q")
        if q:
            filtros = Q(nombre__icontains=q) | Q(raza__icontains=q) | Q(especie__icontains=q)
            if (perfil and perfil.rol == "VET") or user.is_staff or user.is_superuser:
                filtros |= Q(DUENO__username__icontains=q) | Q(DUENO__email__icontains=q)
            qs = qs.filter(filtros)

        return qs.order_by("nombre")
    
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

class MascotaUpdate(DuenoOrVetCanEditMascotaMixin, UpdateView):
    model = Mascota
    form_class = MascotaForm  #  Usar el formulario
    template_name = "mascota/form.html"
    success_url = reverse_lazy("mascota:lista")

class MascotaDelete(DuenoOrVetCanEditMascotaMixin, DeleteView):
    model = Mascota
    template_name = "mascota/confirm_delete.html"
    success_url = reverse_lazy("mascota:lista")