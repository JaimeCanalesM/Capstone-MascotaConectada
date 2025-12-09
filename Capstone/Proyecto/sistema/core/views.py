from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import render, redirect
from django.db.models import Max

# Create your views here.
def index(request):
    # Obtener mascotas que tienen eventos clínicos, ordenadas por la fecha del último evento
    from mascota.models import Mascota
    from historial.models import EventoClinico

    # Obtener IDs de mascotas con eventos clínicos, ordenadas por el evento más reciente
    mascotas_con_eventos = (
        EventoClinico.objects
        .values('mascota')
        .annotate(ultimo_evento=Max('fecha'))
        .order_by('-ultimo_evento')
        [:10]  # Últimas 10 mascotas
    )

    # Obtener las mascotas completas
    mascota_ids = [item['mascota'] for item in mascotas_con_eventos]
    mascotas_carrusel = Mascota.objects.filter(id__in=mascota_ids).select_related('DUENO')

    # Ordenar manualmente según el orden de mascota_ids
    mascotas_ordenadas = sorted(mascotas_carrusel, key=lambda m: mascota_ids.index(m.id))

    return render(request, "index.html", {
        "mascotas_carrusel": mascotas_ordenadas,
    })

def nosotros(request):
    return render(request, "core/nosotros.html")

def contacto(request):
    return render(request, "core/contacto.html")

def privacidad_terminos(request):
    return render(request, "core/privacidad_terminos.html")