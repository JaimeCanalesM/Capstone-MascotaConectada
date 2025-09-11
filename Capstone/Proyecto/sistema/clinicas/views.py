from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def lista_clinicas(request):
    return HttpResponse("lista_clinicas")

def detalle_clinica(request, clinica_id):
    return HttpResponse(f"detalle_clinica {clinica_id}")