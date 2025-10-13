from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def lista(request):
    return render(request, 'mascota/lista.html')

def detalles(request):
    return render(request, 'mascota/detalles.html')

def formas(request):
    return render(request, 'mascota/formas.html')

def confirmar_eliminacion(request):
    return render(request, 'mascota/confirmar_eliminacion.html')

def crear_mascota(request):
    # cuando tengas ModelForm, aquí procesas POST/GET
    return render(request, "mascota/crear.html")



