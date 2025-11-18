# CAMBIOS REALIZADOS EN EL PROYECTO MASCOTACONECTADA

## Fecha: 2025-11-17

---

## 1. MEJORAS DE SEGURIDAD

### 1.1 Variables de Entorno
**Problema**: Credenciales sensibles estaban hardcodeadas en `settings.py`

**Solución Implementada**:
- ✅ Instalado `python-decouple==3.8` para gestión de variables de entorno
- ✅ Creado archivo `.env.example` con plantilla de configuración
- ✅ Actualizado `settings.py` para usar `config()` en lugar de valores hardcodeados

**Variables migradas a entorno**:
- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`
- `GOOGLE_MAPS_API_KEY`

**Archivo modificado**:
- `sistema/settings.py`

**Archivos creados**:
- `.env.example` (plantilla para configuración)
- `requirements.txt` actualizado con `python-decouple==3.8`

**Instrucciones de uso**:
```bash
# 1. Copiar plantilla de configuración
cp .env.example .env

# 2. Editar .env con tus valores reales
# 3. Generar SECRET_KEY nueva:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 4. Pegar la clave en .env
SECRET_KEY=tu-clave-generada-aqui
```

**IMPORTANTE**: El archivo `.env` ya está en `.gitignore` y NO debe subirse a Git.

---

## 2. CAMPO RUT OBLIGATORIO PARA VETERINARIOS

### 2.1 Modelo Perfil Actualizado
**Requerimiento**: Solicitar RUT chileno al registrar veterinarios

**Cambios implementados**:
- ✅ Agregado campo `vet_rut` al modelo `Perfil` (máx 12 caracteres)
- ✅ Creado archivo `cuentas/validators.py` con validación de RUT chileno
- ✅ Implementada validación de dígito verificador (algoritmo estándar chileno)
- ✅ Implementado formateo automático: `12.345.678-9`

**Archivos modificados**:
- `cuentas/models.py` (agregado campo `vet_rut`)
- `cuentas/forms.py` (agregado campo y validación en `UnifiedSignupForm`)
- `cuentas/admin.py` (agregado `vet_rut` a list_display y search_fields)

**Archivos creados**:
- `cuentas/validators.py` (funciones `validar_rut_chileno()` y `formatear_rut()`)

**Migración aplicada**:
```bash
python manage.py makemigrations cuentas
python manage.py migrate
```

**Validaciones implementadas**:
1. RUT obligatorio si `is_veterinario=True`
2. Formato aceptado: `12.345.678-9`, `12345678-9`, o `123456789`
3. Validación de dígito verificador usando algoritmo módulo 11
4. Formateo automático al guardar

**Ejemplo de uso**:
```python
from cuentas.validators import validar_rut_chileno, formatear_rut

# Validar RUT
validar_rut_chileno("12.345.678-9")  # Lanza ValidationError si es inválido

# Formatear RUT
rut_formateado = formatear_rut("123456789")  # Retorna "12.345.678-9"
```

---

## 3. INTEGRACIÓN DE GOOGLE MAPS API

### 3.1 Configuración de la API
**Requerimiento**: Mostrar clínicas en mapa interactivo con geolocalización

**Configuración necesaria**:
1. Obtener Google Maps API Key en: https://console.cloud.google.com/
2. Habilitar las siguientes APIs:
   - Maps JavaScript API
   - Geocoding API
   - Places API

3. Agregar la API Key al archivo `.env`:
```env
GOOGLE_MAPS_API_KEY=tu-api-key-aqui
```

### 3.2 Cambios en el Backend

**Archivos modificados**:
- `clinicas/views.py`:
  - `ClinicaList`: Agregado contexto con `google_maps_api_key` y `clinicas_json`
  - `ClinicaDetail`: Agregado contexto con `google_maps_api_key`
  - Filtrado de clínicas con coordenadas (`lat` y `lng` no nulos)
  - Serialización JSON de clínicas para JavaScript

**Datos enviados al frontend**:
```json
[
  {
    "id": 1,
    "nombre": "Clínica Veterinaria Ejemplo",
    "direccion": "Calle Principal 123",
    "telefono": "+56912345678",
    "lat": -33.4489,
    "lng": -70.6693
  }
]
```

### 3.3 Cambios en el Frontend

**Template actualizado**: `clinicas/templates/clinicas/lista.html`

**Funcionalidades implementadas**:
1. **Mapa interactivo de Google Maps**:
   - Centro inicial: Santiago de Chile (-33.4489, -70.6693)
   - Zoom automático para mostrar todas las clínicas
   - Marcadores rojos para clínicas
   - Marcador azul para ubicación del usuario

2. **Botón "Ubicarme"**:
   - Solicita permiso de geolocalización al usuario
   - Centra el mapa en la ubicación actual
   - Calcula distancias a todas las clínicas (fórmula de Haversine)
   - Re-ordena la lista de clínicas por cercanía
   - Muestra distancia en km en cada tarjeta

3. **Info Windows en marcadores**:
   - Al hacer clic en un marcador, se muestra información de la clínica
   - Botón "Cómo llegar" que abre Google Maps en nueva pestaña
   - Resalta la tarjeta correspondiente en la lista

4. **Lista de clínicas con tarjetas**:
   - Diseño responsivo (col-md-6 col-lg-4)
   - Botón "Ver detalle" → Redirige a `/clinicas/{id}/`
   - Botón "Cómo llegar" → Abre Google Maps con direcciones

**Template actualizado**: `clinicas/templates/clinicas/detalle.html`

**Funcionalidades implementadas**:
- Mapa individual de la clínica (zoom 15)
- Marcador con información
- Info Window mostrado automáticamente
- Botón "Cómo llegar" directo a Google Maps

**Template base actualizado**: `templates/base.html`
- Agregado bloque `{% block extra_js %}` antes de `</body>`

### 3.4 Fórmula de Haversine (Cálculo de Distancias)

La distancia entre dos puntos geográficos se calcula usando:

```javascript
function calcularDistancia(lat1, lng1, lat2, lng2) {
  const R = 6371; // Radio de la Tierra en km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLng/2) * Math.sin(dLng/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c; // Distancia en km
}
```

### 3.5 URLs de Google Maps

**Formato para direcciones**:
```
https://www.google.com/maps/dir/?api=1&destination={lat},{lng}
```

**Ejemplo**:
```html
<a href="https://www.google.com/maps/dir/?api=1&destination=-33.4489,-70.6693" target="_blank">
  Cómo llegar
</a>
```

---

## 4. INSTALACIÓN Y CONFIGURACIÓN

### 4.1 Instalar Dependencias
```bash
cd Capstone/Proyecto
pip install -r requirements.txt
```

**Nueva dependencia**:
- `python-decouple==3.8`

### 4.2 Configurar Variables de Entorno
```bash
# 1. Copiar plantilla
cp .env.example .env

# 2. Editar .env con tus valores
nano .env  # o usar cualquier editor

# 3. Valores mínimos requeridos:
SECRET_KEY=...              # Generar nueva clave
DEBUG=True                  # False en producción
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=mascotaconectada
DB_USER=mc_user
DB_PASSWORD=tu-password
GOOGLE_MAPS_API_KEY=...    # Obtener de Google Cloud Console
```

### 4.3 Aplicar Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4.4 Ejecutar Servidor
```bash
python manage.py runserver
```

---

## 5. VALIDACIÓN DE CAMBIOS

### 5.1 Seguridad
- [ ] Verificar que `.env` está en `.gitignore`
- [ ] Confirmar que no hay credenciales hardcodeadas en el código
- [ ] Generar nueva `SECRET_KEY` para producción
- [ ] Configurar `DEBUG=False` en producción
- [ ] Configurar `ALLOWED_HOSTS` con dominios reales

### 5.2 RUT de Veterinarios
- [ ] Registrar nuevo veterinario con RUT
- [ ] Validar que acepta formato: `12.345.678-9`
- [ ] Validar que rechaza RUT con dígito verificador incorrecto
- [ ] Verificar que el RUT se formatea automáticamente
- [ ] Verificar que el RUT aparece en el panel de admin

### 5.3 Google Maps
- [ ] Verificar que el mapa se carga correctamente en `/clinicas/`
- [ ] Probar botón "Ubicarme" (solicita permiso de geolocalización)
- [ ] Verificar que se calculan distancias correctamente
- [ ] Probar clic en marcadores (abre info window)
- [ ] Verificar botón "Cómo llegar" (abre Google Maps)
- [ ] Probar página de detalle de clínica (`/clinicas/{id}/`)

---

## 6. NOTAS IMPORTANTES

### 6.1 Google Maps API - Límites y Costos
- **Límite gratuito**: $200 USD/mes de crédito
- **Uso típico**: ~28,000 cargas de mapa/mes gratis
- **Recomendación**: Habilitar restricciones de dominio en Google Cloud Console

### 6.2 Validación de RUT
El algoritmo implementado es el estándar chileno:
1. Multiplicadores: 2, 3, 4, 5, 6, 7 (cíclico de derecha a izquierda)
2. Suma de productos
3. Módulo 11
4. Dígito verificador: 11 - resto
5. Casos especiales: 11 → 0, 10 → K

### 6.3 Geolocalización del Usuario
- Requiere **HTTPS** en producción (Chrome/Firefox lo exigen)
- El usuario debe otorgar permiso explícito
- Puede fallar si el GPS está desactivado o en interiores

---

## 7. ARCHIVOS MODIFICADOS (RESUMEN)

### Backend
- ✅ `sistema/settings.py` - Variables de entorno
- ✅ `cuentas/models.py` - Campo `vet_rut`
- ✅ `cuentas/forms.py` - Validación de RUT
- ✅ `cuentas/admin.py` - Mostrar RUT en admin
- ✅ `cuentas/validators.py` - *NUEVO* - Validador de RUT
- ✅ `clinicas/views.py` - Contexto con Google Maps API Key
- ✅ `requirements.txt` - Agregado `python-decouple`

### Frontend
- ✅ `templates/base.html` - Bloque `extra_js`
- ✅ `clinicas/templates/clinicas/lista.html` - Mapa interactivo completo
- ✅ `clinicas/templates/clinicas/detalle.html` - Mapa individual

### Configuración
- ✅ `.env.example` - *NUEVO* - Plantilla de configuración
- ✅ `cuentas/migrations/0003_perfil_vet_rut_alter_perfil_licencia_medica.py` - *NUEVO*

---

## 8. PRÓXIMOS PASOS RECOMENDADOS

### Seguridad
1. Configurar HTTPS en producción
2. Implementar rate limiting en endpoints públicos
3. Agregar logging estructurado (ej: Sentry)
4. Configurar CSRF_TRUSTED_ORIGINS para producción
5. Habilitar SECURE_SSL_REDIRECT en producción

### Google Maps
1. Restringir API Key por dominio en Google Cloud Console
2. Agregar clustering de marcadores si hay muchas clínicas
3. Implementar filtros adicionales (servicios, horarios)
4. Agregar búsqueda por dirección/ciudad
5. Cachear coordenadas de clínicas

### Veterinarios
1. Agregar campo de especialidad (ej: "Cirugía", "Odontología")
2. Permitir subir múltiples documentos
3. Implementar sistema de calificaciones
4. Agregar foto de perfil del veterinario

---

## 9. TROUBLESHOOTING

### Error: "ModuleNotFoundError: No module named 'decouple'"
**Solución**:
```bash
pip install python-decouple
```

### Error: "Google Maps API Key no configurada"
**Solución**:
1. Crear `.env` desde `.env.example`
2. Agregar `GOOGLE_MAPS_API_KEY=tu-key-aqui`
3. Reiniciar servidor Django

### Mapa no se muestra
**Posibles causas**:
1. API Key inválida o sin las APIs habilitadas
2. Dominio no autorizado en Google Cloud Console
3. Clínicas sin coordenadas `lat`/`lng`
4. Error de JavaScript (revisar consola del navegador)

### Geolocalización no funciona
**Posibles causas**:
1. Usuario denegó el permiso
2. Navegador no soporta geolocalización
3. Sitio no está en HTTPS (requerido en producción)

---

## 10. CONTACTO Y SOPORTE

Para dudas o problemas con los cambios implementados, referirse a:
- Documentación de Django: https://docs.djangoproject.com/
- Google Maps JavaScript API: https://developers.google.com/maps/documentation/javascript
- Validación RUT Chile: https://es.wikipedia.org/wiki/Rol_%C3%9Anico_Tributario

---

**Desarrollador**: Claude (Anthropic)
**Fecha**: 17 de noviembre de 2025
**Versión**: 1.0
