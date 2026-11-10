"""Vérifications au démarrage (python manage.py check) des réglages de comptes."""
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.checks import Error, register


@register()
def roles_double_auth(app_configs, **kwargs):
    """Chaque rôle de DOUBLE_AUTH_ROLES doit exister dans ROLES."""
    inconnus = sorted(set(settings.DOUBLE_AUTH_ROLES) - set(settings.ROLES))
    if not inconnus:
        return []
    return [
        Error(
            f"DOUBLE_AUTH_ROLES contient des rôles absents de ROLES : {', '.join(inconnus)}.",
            hint="Corriger DOUBLE_AUTH_ROLES ou ROLES dans le fichier .env.",
            id="comptes.E001",
        )
    ]


@register()
def cles_chiffrement_double_auth(app_configs, **kwargs):
    """MFA_CLES_CHIFFREMENT doit contenir au moins une clé Fernet valide (32 octets en base64)."""
    erreur = None
    if not settings.MFA_CLES_CHIFFREMENT:
        erreur = "MFA_CLES_CHIFFREMENT est vide."
    else:
        for cle in settings.MFA_CLES_CHIFFREMENT:
            try:
                Fernet(cle)
            except ValueError:
                erreur = "MFA_CLES_CHIFFREMENT contient une clé invalide."
                break
    if erreur is None:
        return []
    return [Error(erreur, hint="Générer une clé : voir la commande dans .env.example.", id="comptes.E002")]
