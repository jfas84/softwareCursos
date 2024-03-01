from django.apps import AppConfig
from django.db.models.signals import post_save

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Importar o código de sinal aqui para garantir que seja executado
        from . import signals
