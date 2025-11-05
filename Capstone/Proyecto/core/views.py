from django.shortcuts import render

def index(request):
    return render(request, "index.html")
def nosotros(request):
    return render(request, "core/nosotros.html")