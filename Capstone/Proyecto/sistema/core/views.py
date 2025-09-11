from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import render, redirect

# Create your views here.
def home(request):
    return render(request, 'index.html')

def nosotros(request):
    return render(request, 'nosotros.html')

def privacidad_terminos(request):
    return render(request, 'privacidad_terminos.html')

def contacto(request):
    return render(request, 'contacto.html')