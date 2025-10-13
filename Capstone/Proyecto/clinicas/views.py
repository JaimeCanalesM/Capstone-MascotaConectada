from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Clinica

class ClinicaList(ListView):
    model = Clinica
    template_name = "clinicas/lista.html"
    context_object_name = "clinicas"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                Q(nombre__icontains=q) |
                Q(direccion__icontains=q) |
                Q(servicios__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx

class ClinicaDetail(DetailView):
    model = Clinica
    template_name = "clinicas/detalle.html"
    context_object_name = "clinica"
