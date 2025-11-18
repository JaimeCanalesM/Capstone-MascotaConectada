# cuentas/validators.py
import re
from django.core.exceptions import ValidationError


def validar_rut_chileno(rut):
    """
    Valida un RUT chileno.
    Acepta formatos: 12.345.678-9, 12345678-9, 123456789
    """
    if not rut:
        return

    # Remover puntos y guiones
    rut_limpio = rut.replace(".", "").replace("-", "").upper()

    # Validar formato básico
    if not re.match(r'^\d{7,8}[0-9K]$', rut_limpio):
        raise ValidationError(
            'RUT inválido. Formato esperado: 12.345.678-9 o 12345678-9'
        )

    # Separar número y dígito verificador
    rut_numeros = rut_limpio[:-1]
    digito_verificador = rut_limpio[-1]

    # Calcular dígito verificador esperado
    suma = 0
    multiplicador = 2

    for digito in reversed(rut_numeros):
        suma += int(digito) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2

    resto = suma % 11
    dv_esperado = 11 - resto

    if dv_esperado == 11:
        dv_esperado = '0'
    elif dv_esperado == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(dv_esperado)

    # Validar
    if digito_verificador != dv_esperado:
        raise ValidationError(
            'RUT inválido. El dígito verificador no corresponde.'
        )


def formatear_rut(rut):
    """
    Formatea un RUT al formato estándar: 12.345.678-9
    """
    if not rut:
        return ""

    # Limpiar
    rut_limpio = rut.replace(".", "").replace("-", "").upper()

    # Separar
    rut_numeros = rut_limpio[:-1]
    dv = rut_limpio[-1]

    # Formatear con puntos
    rut_formateado = ""
    for i, digito in enumerate(reversed(rut_numeros)):
        if i > 0 and i % 3 == 0:
            rut_formateado = "." + rut_formateado
        rut_formateado = digito + rut_formateado

    return f"{rut_formateado}-{dv}"
