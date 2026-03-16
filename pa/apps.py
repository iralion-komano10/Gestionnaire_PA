from django.apps import AppConfig

class PaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pa'
    
    def ready(self):
        from . import scheduler
        scheduler.start_scheduler()