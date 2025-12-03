# GUÍA RÁPIDA DE INSTALACIÓN

## MascotaConectada - Setup Rápido

---

## 1. INSTALAR DEPENDENCIAS

```bash
cd Capstone/Proyecto
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 2. CONFIGURAR VARIABLES DE ENTORNO

```bash
# Copiar plantilla
cp .env.example .env
```

**Editar `.env` con tus valores**:

```env
# Generar nueva SECRET_KEY con:
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY=pega-aqui-la-clave-generada

DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (ajustar según tu configuración MySQL)
DB_NAME=mascotaconectada
DB_USER=mc_user
DB_PASSWORD=tu-password
DB_HOST=127.0.0.1
DB_PORT=3306

# Google Maps API Key (obtener en: https://console.cloud.google.com/)
GOOGLE_MAPS_API_KEY=tu-google-maps-api-key
```

---

## 3. OBTENER GOOGLE MAPS API KEY

1. Ir a: https://console.cloud.google.com/
2. Crear proyecto nuevo (o usar existente)
3. Habilitar las siguientes APIs:
   - **Maps JavaScript API**
   - **Geocoding API**
   - **Places API**
4. Crear credenciales → API Key
5. Copiar la API Key al archivo `.env`

**IMPORTANTE**: Restringir la API Key por dominio en producción

---

## 4. APLICAR MIGRACIONES

```bash
python manage.py migrate
```

---

## 5. CREAR SUPERUSUARIO (OPCIONAL)

```bash
python manage.py createsuperuser
```

---

## 6. EJECUTAR SERVIDOR

```bash
python manage.py runserver
```

**Acceso**:
- Frontend: http://localhost:8000/
- Admin: http://localhost:8000/admin/

---

## 7. VERIFICAR FUNCIONALIDADES

###  Seguridad
- Variables de entorno configuradas
- No hay credenciales en el código

###  Registro de Veterinarios
- Ir a: http://localhost:8000/cuentas/registro/
- Marcar "Soy veterinario"
- Completar RUT (ej: 12.345.678-5)
- Subir título de médico veterinario
- Registrar

###  Google Maps
- Ir a: http://localhost:8000/clinicas/
- Ver mapa interactivo
- Hacer clic en "Ubicarme" (otorgar permiso)
- Ver clínicas ordenadas por cercanía

---

## PROBLEMAS COMUNES

### Error: "No module named 'decouple'"
```bash
pip install python-decouple
```

### Mapa no se muestra
- Verificar que `GOOGLE_MAPS_API_KEY` está en `.env`
- Verificar que las APIs están habilitadas en Google Cloud Console
- Revisar consola del navegador (F12) para errores de JavaScript

### RUT inválido
- Formato aceptado: `12.345.678-9`, `12345678-9`, o `123456789`
- El dígito verificador debe ser correcto

---
