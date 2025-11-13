from django.apps import AppConfig

class HistorialConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "historial"
    
    def ready(self):
        """
        Se ejecuta cuando la app se inicializa.
        """
        # Importar y configurar signals
        from historial.signals import setup_signals
        setup_signals()
    