from django.apps import AppConfig


class CuentasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cuentas'

    def ready(self):
        # Importar signals cuando la app esté lista
        import cuentas.signals
