from django.apps import AppConfig


class JournalConfig(AppConfig):
    name = "journal"
    verbose_name = "Journal d'accès"

    def ready(self):
        from . import signaux  # noqa: F401  (branche l'enregistrement des connexions)
