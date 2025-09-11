from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def perfil(request):
    return render(request, 'cuentas/perfil.html')

def login(request):
    return render(request, 'registro/login.html')

def registro(request):
    return render(request, 'cuentas/registro.html')

