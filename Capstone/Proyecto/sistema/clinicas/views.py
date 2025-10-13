from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def lista_clinicas(request):
    return render(request, "clinicas/lista.html")

def detalle_clinica(request, clinica_id):
    return HttpResponse(f"detalle_clinica {clinica_id}")