from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, DeleteView, DetailView, CreateView
from django.urls import reverse_lazy
from django.db.models import Q
from cuentas.mixins import DuenoOrVetCanEditMascotaMixin
from .models import Mascota

class MascotaList(LoginRequiredMixin, ListView):
    model = Mascota
    template_name = "mascota/lista.html"
    context_object_name = "mascotas"
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        qs = Mascota.objects.select_related("dueno").all()

        # DUENO: solo sus mascotas
        if not (perfil and perfil.rol == "VET") and not user.is_staff and not user.is_superuser:
            qs = qs.filter(dueno=user)

        q = self.request.GET.get("q")
        if q:
            filtros = Q(nombre__icontains=q) | Q(raza__icontains=q) | Q(especie__icontains=q)
            if (perfil and perfil.rol == "VET") or user.is_staff or user.is_superuser:
                filtros |= Q(dueno__username__icontains=q) | Q(dueno__email__icontains=q)
            qs = qs.filter(filtros)

        return qs.order_by("nombre")
    
class MascotaDetail(LoginRequiredMixin, DetailView):
    model = Mascota
    template_name = "mascota/detalle.html"
    context_object_name = "mascota"

    def get_queryset(self):
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        qs = Mascota.objects.select_related("dueno")
        if (perfil and perfil.rol == "VET") or user.is_staff or user.is_superuser:
            return qs
        return qs.filter(dueno=user)
    
class MascotaCreate(LoginRequiredMixin, CreateView):
    model = Mascota
    # Incluimos 'dueno' para VET/STAFF. Para DUENO lo ocultamos y lo seteamos automáticamente.
    fields = ["dueno", "nombre", "especie", "raza", "sexo", "fecha_nacimiento", "peso", "foto", "notas"]
    template_name = "mascota/form.html"
    success_url = reverse_lazy("mascota:lista")

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        # Si NO es VET/STAFF, ocultamos/quitamos el campo 'dueno' del form
        if not ((perfil and perfil.rol == "VET") or user.is_staff or user.is_superuser):
            form.fields.pop("dueno", None)
        return form

    def form_valid(self, form):
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        # Si es dueño normal, fuerza que la mascota le pertenezca
        if not ((perfil and perfil.rol == "VET") or user.is_staff or user.is_superuser):
            form.instance.dueno = user
        return super().form_valid(form)

class MascotaUpdate(DuenoOrVetCanEditMascotaMixin, UpdateView):
    model = Mascota
    fields = ["nombre", "especie", "raza", "sexo", "fecha_nacimiento", "peso", "foto", "notas"]
    template_name = "mascota/form.html"
    success_url = reverse_lazy("mascota:lista")

class MascotaDelete(DuenoOrVetCanEditMascotaMixin, DeleteView):
    model = Mascota
    template_name = "mascota/confirm_delete.html"
    success_url = reverse_lazy("mascota:lista")