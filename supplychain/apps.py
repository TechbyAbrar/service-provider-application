from django.apps import AppConfig

class SupplychainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'supplychain'

    def ready(self):
        import supplychain.signals  # ensures signals are registered
