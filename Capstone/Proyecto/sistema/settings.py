# sistema/settings.py
from pathlib import Path
import os
from decouple import config, Csv


BASE_DIR = Path(__file__).resolve().parent.parent

# SEGURIDAD: Usando variables de entorno
SECRET_KEY = config('SECRET_KEY', default='dev-inseguro-cambia-esto')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Aplicaciones del proyecto
    "core",
    "clinicas",
    "cuentas",
    "mascota",
    "panel",
    "citas",
    "historial",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sistema.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [ BASE_DIR / "templates" ],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
    },
}]

WSGI_APPLICATION = "sistema.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": config('DB_ENGINE', default='django.db.backends.mysql'),
        "NAME": config('DB_NAME', default='mascotaconectada'),
        "USER": config('DB_USER', default='mc_user'),
        "PASSWORD": config('DB_PASSWORD', default='mc_password_123'),
        "HOST": config('DB_HOST', default='127.0.0.1'),
        "PORT": config('DB_PORT', default='3306'),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

LANGUAGE_CODE = "es"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"


#  MEDIA - para subidas de usuarios (fotos de mascotas, etc)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/cuentas/redireccion/"
LOGOUT_REDIRECT_URL = "/"

EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@mascotaconectada.cl")

# Producción (cuando tengas SMTP real)
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)

# Google Maps API Key
GOOGLE_MAPS_API_KEY = config("GOOGLE_MAPS_API_KEY", default="")