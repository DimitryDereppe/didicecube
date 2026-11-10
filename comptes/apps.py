from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ComptesConfig(AppConfig):
    name = "comptes"
    verbose_name = "Comptes"

    def ready(self):
        # Après chaque "migrate", on s'assure que chaque rôle de settings.ROLES a son groupe.
        from . import checks  # noqa: F401  (vérifie DOUBLE_AUTH_ROLES au démarrage)
        from .roles import cree_groupes_des_roles

        post_migrate.connect(cree_groupes_des_roles, sender=self)
