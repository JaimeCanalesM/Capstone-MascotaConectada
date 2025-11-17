from django.shortcuts import render
from mascota.models import Mascota
from django.db.models.functions import Random

def index(request):
    mascotas_con_foto = (
        Mascota.objects
        .exclude(foto__isnull=True)
        .exclude(foto__exact="")
        .order_by(Random())[:5]
    )

    return render(request, "index.html", {
        "mascotas_carrusel": mascotas_con_foto,
    })
    
def nosotros(request):
    return render(request, "core/nosotros.html")

