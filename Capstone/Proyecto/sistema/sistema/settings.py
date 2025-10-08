"""
settings.py — MascotaConectada
Django 5.x – Perfil de desarrollo y producción con variables de entorno.
"""

from pathlib import Path
import os
from urllib.parse import urlparse

# --------------------------------------------------------------------------------------
# RUTAS BASE
# --------------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # .../Proyecto/sistema

# --------------------------------------------------------------------------------------
# VARIABLES DE ENTORNO (con valores por defecto seguros para DEV)
# En Windows/Linux/Mac/PythonAnywhere exporta antes de ejecutar:
#   set DJANGO_SECRET_KEY="xxx" / export DJANGO_SECRET_KEY="xxx"
#   set DJANGO_DEBUG=0/1
#   set DJANGO_ALLOWED_HOSTS="jaime.pythonanywhere.com,localhost,127.0.0.1"
# --------------------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "DEV-KEY-INSEGURA-cambia-esto-en-produccion"
)

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# Lista separada por comas. En DEV permitimos todo por simpleza.
if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    _hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "")
    ALLOWED_HOSTS = [h.strip() for h in _hosts.split(",") if h.strip()]

# Si despliegas en dominio propio / PythonAnywhere agrega aquí (o vía env):
#   export DJANGO_CSRF_TRUSTED_ORIGINS="https://tudominio.com,https://tusubdominio.pythonanywhere.com"
_csrf = os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf.split(",") if o.strip()]

# --------------------------------------------------------------------------------------
# APPS
# --------------------------------------------------------------------------------------
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Apps del proyecto
    "core",
    "cuentas",
    "mascota",
    "clinicas",
    "citas",

    # (Opcional) Si luego agregas CORS para Angular SPA:
    # "corsheaders",
]

# --------------------------------------------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # (Opcional) si usas WhiteNoise para estáticos en prod:
    # "whitenoise.middleware.WhiteNoiseMiddleware",

    # (Opcional) si activas CORS:
    # "corsheaders.middleware.CorsMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# (Opcional) CORS básico si consumes API desde Angular en otro dominio:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:4200",
#     "https://tu-frontend.com",
# ]

# --------------------------------------------------------------------------------------
# URLS & WSGI
# --------------------------------------------------------------------------------------
ROOT_URLCONF = "sistema.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Puedes tener plantillas por app y además una carpeta global /templates
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.auth_forms",
            ],
        },
    },
]

WSGI_APPLICATION = "sistema.wsgi.application"

# --------------------------------------------------------------------------------------
# BASE DE DATOS
# Por defecto: SQLite (desarrollo). Producción: MySQL (opcional abajo).
# Control por env:
#   DJANGO_DB_URL="sqlite:///db.sqlite3"
#   o "mysql://usuario:clave@host:3306/nombre_bd"
# Si no defines DJANGO_DB_URL, se usa SQLite local.
# --------------------------------------------------------------------------------------
def _db_from_env():
    db_url = os.environ.get("DJANGO_DB_URL")
    if not db_url:
        # SQLite por defecto
        return {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }

    parsed = urlparse(db_url)
    if parsed.scheme.startswith("mysql"):
        return {
            "default": {
                "ENGINE": "django.db.backends.mysql",
                "NAME": parsed.path.lstrip("/") or os.environ.get("MYSQL_DATABASE", ""),
                "USER": parsed.username or os.environ.get("MYSQL_USER", ""),
                "PASSWORD": parsed.password or os.environ.get("MYSQL_PASSWORD", ""),
                "HOST": parsed.hostname or os.environ.get("MYSQL_HOST", "127.0.0.1"),
                "PORT": parsed.port or os.environ.get("MYSQL_PORT", "3306"),
                "OPTIONS": {
                    "charset": "utf8mb4",
                    "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
                },
            }
        }

    if parsed.scheme.startswith("sqlite"):
        name = parsed.path.lstrip("/") or "db.sqlite3"
        return {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / name,
            }
        }

    # Fallback muy básico
    return {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

DATABASES = _db_from_env()

# EJEMPLO PythonAnywhere (sin DJANGO_DB_URL, usando variables sueltas)
# if os.environ.get("PA_MYSQL_NAME"):  # habilítalo si te acomoda esta vía
#     DATABASES = {
#         "default": {
#             "ENGINE": "django.db.backends.mysql",
#             "NAME": os.environ.get("PA_MYSQL_NAME"),
#             "USER": os.environ.get("PA_MYSQL_USER"),
#             "PASSWORD": os.environ.get("PA_MYSQL_PASSWORD"),
#             "HOST": os.environ.get("PA_MYSQL_HOST", "127.0.0.1"),
#             "PORT": os.environ.get("PA_MYSQL_PORT", "3306"),
#             "OPTIONS": {"charset": "utf8mb4"},
#         }
#     }

# --------------------------------------------------------------------------------------
# AUTH / PASSWORD VALIDATORS
# --------------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Redirecciones de login/logout
LOGIN_URL = "login"  # usando las auth views built-in
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# --------------------------------------------------------------------------------------
# INTERNACIONALIZACIÓN
# --------------------------------------------------------------------------------------
LANGUAGE_CODE = "es-cl"  # español Chile
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / "locale"]

# Formato de fecha/hora (opcional)
# DATETIME_FORMAT = "d/m/Y H:i"
# DATE_FORMAT = "d/m/Y"

# --------------------------------------------------------------------------------------
# ARCHIVOS ESTÁTICOS & MEDIA
# --------------------------------------------------------------------------------------
# En desarrollo, Django sirve static automáticamente con runserver.
STATIC_URL = "/static/"
# Carpeta donde pondrás tus assets globales (además de app/static/)
STATICFILES_DIRS = [
    BASE_DIR / "core" / "static",
]
# Destino de collectstatic (producción: PythonAnywhere, etc.)
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media (subidas de usuarios)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# (Opcional) Si usas WhiteNoise para servir estáticos en prod, habilita middleware y:
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --------------------------------------------------------------------------------------
# MENSAJES -> mapeo a Bootstrap 5
# --------------------------------------------------------------------------------------
from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

# --------------------------------------------------------------------------------------
# EMAIL
# Por defecto en DEV: consola. En prod configura SMTP vía env.
# --------------------------------------------------------------------------------------
EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend" if DEBUG else "django.core.mail.backends.smtp.EmailBackend",
)

EMAIL_HOST = os.environ.get("DJANGO_EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("DJANGO_EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("DJANGO_EMAIL_USE_TLS", "1") == "1"
DEFAULT_FROM_EMAIL = os.environ.get("DJANGO_DEFAULT_FROM_EMAIL", "no-reply@mascotaconectada.local")

# --------------------------------------------------------------------------------------
# SEGURIDAD (se aplican cuando DEBUG=False)
# --------------------------------------------------------------------------------------
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SSL_REDIRECT", "1") == "1"

    # HTTP Strict Transport Security (HSTS)
    SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_HSTS_SECONDS", "31536000"))  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Cabeceras
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

# --------------------------------------------------------------------------------------
# LOGGING
# --------------------------------------------------------------------------------------
LOG_LEVEL = os.environ.get("DJANGO_LOG_LEVEL", "INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[{levelname}] {asctime} {name} :: {message}", "style": "{"},
        "simple": {"format": "[{levelname}] {message}", "style": "{"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose" if not DEBUG else "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING" if not DEBUG else "INFO",  # en DEV puedes subir a DEBUG para ver queries
        },
    },
}

# --------------------------------------------------------------------------------------
# AUTO FIELD
# --------------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
