from django.apps import AppConfig


class CubeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cube"
    verbose_name = "Cube"

    def ready(self):
        from . import signaux  # noqa: F401  (efface les fichiers des skins supprimés)
