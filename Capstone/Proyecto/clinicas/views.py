from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.conf import settings
from .models import Clinica

class ClinicaList(ListView):
    model = Clinica
    template_name = "clinicas/lista.html"
    context_object_name = "clinicas"
    paginate_by = 100  # Aumentado para mostrar todas en el mapa

    def get_queryset(self):
        qs = super().get_queryset()
        # Solo clínicas con coordenadas para el mapa
        qs = qs.filter(lat__isnull=False, lng__isnull=False)

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
        ctx["google_maps_api_key"] = settings.GOOGLE_MAPS_API_KEY

        # Preparar datos para el mapa
        clinicas_json = []
        for clinica in ctx["clinicas"]:
            if clinica.lat and clinica.lng:
                clinicas_json.append({
                    "id": clinica.id,
                    "nombre": clinica.nombre,
                    "direccion": clinica.direccion,
                    "telefono": clinica.telefono,
                    "lat": float(clinica.lat),
                    "lng": float(clinica.lng),
                })

        import json
        ctx["clinicas_json"] = json.dumps(clinicas_json)

        return ctx

class ClinicaDetail(DetailView):
    model = Clinica
    template_name = "clinicas/detalle.html"
    context_object_name = "clinica"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["google_maps_api_key"] = settings.GOOGLE_MAPS_API_KEY
        return ctx
