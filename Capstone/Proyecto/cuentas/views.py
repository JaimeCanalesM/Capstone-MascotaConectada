from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import View
from .forms import SignupDuenoForm, SignupVetForm
from .models import Perfil

class SignupDuenoView(View):
    template_name = "cuentas/registro_dueno.html"
    def get(self, request):
        return render(request, self.template_name, {"form": SignupDuenoForm()})
    def post(self, request):
        form = SignupDuenoForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("cuentas:redireccion")
        return render(request, self.template_name, {"form": form})

class SignupVetView(View):
    template_name = "cuentas/registro_vet.html"
    def get(self, request):
        return render(request, self.template_name, {"form": SignupVetForm()})
    def post(self, request):
        form = SignupVetForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("cuentas:redireccion")
        return render(request, self.template_name, {"form": form})

@login_required
def redireccion_post_login(request):
    """ Redirige según rol/estado. """
    perfil = getattr(request.user, "perfil", None)
    if not perfil:
        return redirect("core:index")

    if perfil.rol == Perfil.ROL_VET:
        # Si es vet y está aprobado, puedes enviarlo a zona vet (cuando exista).
        # Por ahora, lo mandamos a clínicas igual, pero mostramos el estado en la UI.
        return redirect("clinicas:lista")

    # Dueño: al home
    return redirect("core:index")
