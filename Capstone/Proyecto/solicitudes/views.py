from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.db.models import Q
from .models import Solicitud
from .forms import SolicitudForm


class SolicitudListView(LoginRequiredMixin, ListView):
    """Vista para listar solicitudes del usuario o todas (si es staff)"""
    model = Solicitud
    template_name = 'solicitudes/lista.html'
    context_object_name = 'solicitudes'
    paginate_by = 10

    def get_queryset(self):
        # Usuarios ven solo sus solicitudes, staff ve todas
        if self.request.user.is_staff:
            qs = Solicitud.objects.all().select_related('usuario', 'mascota')
        else:
            qs = Solicitud.objects.filter(usuario=self.request.user).select_related('mascota')

        # Filtros opcionales
        estado = self.request.GET.get('estado')
        if estado:
            qs = qs.filter(estado=estado)

        tipo = self.request.GET.get('tipo')
        if tipo:
            qs = qs.filter(tipo=tipo)

        # Búsqueda
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(asunto__icontains=q) | Q(descripcion__icontains=q)
            )

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['estado_actual'] = self.request.GET.get('estado', '')
        ctx['tipo_actual'] = self.request.GET.get('tipo', '')
        ctx['q'] = self.request.GET.get('q', '')

        # Contadores para el usuario
        if self.request.user.is_staff:
            base_qs = Solicitud.objects.all()
        else:
            base_qs = Solicitud.objects.filter(usuario=self.request.user)

        ctx['total_solicitudes'] = base_qs.count()
        ctx['pendientes'] = base_qs.filter(estado=Solicitud.ESTADO_PENDIENTE).count()
        ctx['en_revision'] = base_qs.filter(estado=Solicitud.ESTADO_EN_REVISION).count()
        ctx['resueltas'] = base_qs.filter(estado=Solicitud.ESTADO_RESUELTA).count()

        return ctx


class SolicitudCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear nueva solicitud"""
    model = Solicitud
    form_class = SolicitudForm
    template_name = 'solicitudes/crear.html'
    success_url = reverse_lazy('solicitudes:lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(
            self.request,
            '✅ Solicitud enviada correctamente. El equipo de administración te responderá pronto.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Por favor, corrige los errores en el formulario.'
        )
        return super().form_invalid(form)


class SolicitudDetailView(LoginRequiredMixin, DetailView):
    """Vista para ver detalle de una solicitud"""
    model = Solicitud
    template_name = 'solicitudes/detalle.html'
    context_object_name = 'solicitud'

    def get_queryset(self):
        # Usuarios ven solo sus solicitudes, staff ve todas
        if self.request.user.is_staff:
            return Solicitud.objects.all().select_related('usuario', 'mascota')
        return Solicitud.objects.filter(usuario=self.request.user).select_related('mascota')
