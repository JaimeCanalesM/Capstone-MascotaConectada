def auth_forms(request):
    # Importar aquí evita ciclos de importación
    from cuentas.forms import MCAuthenticationForm, MCUserCreationForm
    return {
        "login_form": MCAuthenticationForm(request=request),
        "register_form": MCUserCreationForm(),
    }
