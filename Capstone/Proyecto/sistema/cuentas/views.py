from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import MCAuthenticationForm, MCUserCreationForm

class MCLoginView(LoginView):
    template_name = "registration/login.html"  # fallback si alguien entra directo a /cuentas/login/
    form_class = MCAuthenticationForm

    def form_valid(self, form):
        response = super().form_valid(form)
        remember = self.request.POST.get("remember_me")
        self.request.session.set_expiry(60*60*24*30 if remember else 0)
        return response

def registro(request):
    if request.user.is_authenticated:
        return redirect("cuentas:perfil")
    if request.method == "POST":
        form = MCUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu cuenta fue creada. ¡Ahora puedes iniciar sesión!")
            return redirect("cuentas:login")
    else:
        form = MCUserCreationForm()
    return render(request, "cuentas/registro.html", {"form": form})

@login_required
def perfil(request):
    return render(request, "cuentas/perfil.html")
