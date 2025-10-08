from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def lista_citas(request):
    return render(request, "citas/lista.html")

def forma_cita(request):
    return render(request, 'citas/forma_cita.html')

def confirmar_eliminar_cita(request):
    return render(request, 'citas/confirmar_eliminar_cita.html')