from django.apps import AppConfig


class MonDemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mon_dem'
    
    def ready(self):
        import mon_dem.algo_devis
