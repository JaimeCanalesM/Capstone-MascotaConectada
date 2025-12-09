# Configuración de Emails - MascotaConectada

Este documento explica las funcionalidades de envío de correos electrónicos implementadas en el sistema.

## Funcionalidades Implementadas

### 1. Notificación a Veterinarios (Automático)

Cuando un administrador aprueba o rechaza la solicitud de un veterinario, el sistema envía automáticamente un correo electrónico al usuario.

#### ¿Cuándo se envía?
- Al cambiar el estado de `vet_estado` de **PENDIENTE** a **APROBADO**
- Al cambiar el estado de `vet_estado` de **PENDIENTE** a **RECHAZADO**

#### ¿Qué información incluye?
- **Aprobación**: Felicitación, datos del perfil, funcionalidades disponibles
- **Rechazo**: Información del motivo (si se agregaron observaciones), pasos a seguir

#### Archivos relacionados:
- `cuentas/signals.py` - Lógica de detección de cambio de estado
- `templates/emails/veterinario_aprobado.html` - Template de aprobación
- `templates/emails/veterinario_rechazado.html` - Template de rechazo

---

### 2. Recordatorios de Citas (Manual/Automático)

Envía recordatorios por correo electrónico a los dueños de mascotas que tienen citas programadas para el día siguiente.

#### ¿Cómo funciona?
El sistema busca todas las citas que:
- Están programadas para **mañana** (día siguiente)
- Tienen estado **PENDIENTE** o **CONFIRMADA**
- Envía un correo con todos los detalles de la cita

#### ¿Qué información incluye?
- Nombre de la mascota
- Fecha y hora de la cita
- Motivo de la cita
- Información de la clínica (nombre, dirección, teléfono)
- Nombre del veterinario asignado
- Consejos para la cita

## Uso del Comando de Recordatorios

### Ejecutar Manualmente

Para enviar recordatorios manualmente:

```bash
# Navega al directorio del proyecto
cd C:\Users\Jaime\Desktop\Capstone-MascotaConectada\Capstone\Proyecto\sistema

# Activa el entorno virtual (si lo usas)
..\..\.venv\Scripts\activate

# Ejecuta el comando
python manage.py enviar_recordatorios_citas
```

### Modo Prueba (Dry Run)

Para ver qué correos se enviarían SIN enviarlos realmente:

```bash
python manage.py enviar_recordatorios_citas --dry-run
```

Esto mostrará:
- Cuántas citas se procesarían
- A qué correos se enviarían
- Sin enviar correos reales

### Automatización con Tareas Programadas

#### Windows (Task Scheduler)

1. Abre el **Programador de tareas** de Windows
2. Crea una nueva tarea básica
3. Configura:
   - **Nombre**: Recordatorios Citas MascotaConectada
   - **Desencadenador**: Diariamente a las 18:00 (o la hora que prefieras)
   - **Acción**: Iniciar un programa
   - **Programa**: `C:\Users\Jaime\Desktop\Capstone-MascotaConectada\Capstone\Proyecto\.venv\Scripts\python.exe`
   - **Argumentos**: `manage.py enviar_recordatorios_citas`
   - **Iniciar en**: `C:\Users\Jaime\Desktop\Capstone-MascotaConectada\Capstone\Proyecto\sistema`

#### Linux/Mac (Cron)

Edita el crontab:
```bash
crontab -e
```

Agrega esta línea para ejecutar diariamente a las 18:00:
```
0 18 * * * cd /ruta/al/proyecto/sistema && /ruta/al/venv/bin/python manage.py enviar_recordatorios_citas
```

## Configuración de Email (settings.py)

El sistema usa las siguientes variables de entorno para configurar el envío de emails:

### Variables de Entorno

```bash
# Backend de email (consola para desarrollo, SMTP para producción)
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# Configuración SMTP (ejemplo con Gmail)
DJANGO_EMAIL_HOST=smtp.gmail.com
DJANGO_EMAIL_PORT=587
DJANGO_EMAIL_USER=tu-email@gmail.com
DJANGO_EMAIL_PASSWORD=tu-contraseña-de-aplicacion
DJANGO_EMAIL_USE_TLS=1
DJANGO_DEFAULT_FROM_EMAIL=noreply@mascotaconectada.cl
```

### Configuración para Gmail

Si usas Gmail, necesitas generar una **contraseña de aplicación**:

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Seguridad → Verificación en dos pasos (actívala si no la tienes)
3. Contraseñas de aplicaciones
4. Genera una nueva contraseña para "Correo" en "Otro dispositivo"
5. Usa esa contraseña en `DJANGO_EMAIL_PASSWORD`

### Modo Desarrollo (Consola)

Por defecto en desarrollo, los correos se muestran en la consola (no se envían):

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Esto es útil para probar sin enviar correos reales.

## Estructura de Archivos

```
Proyecto/
├── cuentas/
│   ├── signals.py                    # Señales para veterinarios
│   └── apps.py                       # Configuración para cargar signals
├── citas/
│   └── management/
│       └── commands/
│           └── enviar_recordatorios_citas.py  # Comando de recordatorios
└── templates/
    └── emails/
        ├── veterinario_aprobado.html      # Template aprobación vet
        ├── veterinario_rechazado.html     # Template rechazo vet
        └── recordatorio_cita.html         # Template recordatorio cita
```

## Probar el Sistema

### 1. Probar Notificación de Veterinarios

1. Crea un usuario con rol veterinario (estado PENDIENTE)
2. Desde el panel admin, cambia el estado a APROBADO o RECHAZADO
3. Verifica que se envió el correo (consola o bandeja de entrada)

### 2. Probar Recordatorios de Citas

```bash
# Ver qué citas se procesarían
python manage.py enviar_recordatorios_citas --dry-run

# Enviar los recordatorios
python manage.py enviar_recordatorios_citas
```

## Logs y Monitoreo

El comando de recordatorios muestra información útil:

```
Encontradas 5 citas para mañana.
   Correo enviado a: usuario1@email.com - Cita(Rex @ 2025-12-09 10:00)
   Correo enviado a: usuario2@email.com - Cita(Luna @ 2025-12-09 14:30)
  ...
 Recordatorios enviados exitosamente: 5
```

En caso de errores:
```
  Error enviando a usuario3@email.com: SMTPAuthenticationError
 Errores: 1
```

##  Solución de Problemas

### Los correos no se envían

1. Verifica las variables de entorno de email
2. Asegúrate de que `EMAIL_BACKEND` esté configurado correctamente
3. Revisa que la contraseña de aplicación sea válida
4. Verifica que el firewall permita conexiones SMTP

### Los correos llegan a spam

1. Configura SPF y DKIM en tu dominio
2. Usa un servicio profesional de email (SendGrid, Mailgun, AWS SES)
3. Asegúrate de que `DEFAULT_FROM_EMAIL` use un dominio válido

##  Notas Adicionales

- Los correos usan templates HTML con estilos inline para mejor compatibilidad
- El sistema es tolerante a fallos: si un correo falla, continúa con los siguientes
- Los recordatorios solo se envían para citas del día siguiente (24 horas antes)
- Las señales de veterinarios se ejecutan automáticamente, no requieren configuración adicional
