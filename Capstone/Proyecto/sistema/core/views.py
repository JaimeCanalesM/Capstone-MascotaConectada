from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import render, redirect

# Create your views here.
def index(request):
    return render(request, "index.html")

def nosotros(request):
    return render(request, "core/nosotros.html")

def contacto(request):
    return render(request, "core/contacto.html")

def privacidad_terminos(request):
    return render(request, "core/privacidad_terminos.html")