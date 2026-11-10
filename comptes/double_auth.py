"""Double authentification, fournie par le module MFA de django-allauth.

Seconds facteurs acceptés, du plus sûr au moins sûr :
1. clé de sécurité ou passkey (WebAuthn) : résiste à l'hameçonnage, car liée à l'adresse du site ;
2. application d'authentification (Aegis, FreeOTP, Google Authenticator…) : code à 6 chiffres ;
3. codes de secours : créés automatiquement avec le premier facteur, à usage unique, montrés une seule fois.

Règles du socle :
- obligatoire pour les superutilisateurs et pour les rôles de settings.DOUBLE_AUTH_ROLES (comptes/middleware.py) ;
- possible pour tous les autres, depuis « Mon compte » ;
- les secrets (clé de l'application, graine des codes de secours) sont chiffrés en base avec MFA_CLES_CHIFFREMENT ;
- quand elle est obligatoire, on ne peut pas retirer son dernier facteur (application) ; pour une clé de sécurité,
  allauth ne demande pas notre avis, mais le middleware renvoie alors aussitôt vers l'activation.
Si tout est perdu, un administrateur supprime les « Authenticators » de la personne dans l'admin ;
elle refait l'activation à sa prochaine connexion.
"""
from allauth.mfa.adapter import DefaultMFAAdapter
from allauth.mfa.models import Authenticator
from cryptography.fernet import Fernet, MultiFernet
from django.conf import settings

from .roles import a_le_role

# Facteurs qui comptent comme une double authentification active (les codes de secours seuls ne suffisent pas).
SECONDS_FACTEURS = (Authenticator.Type.WEBAUTHN, Authenticator.Type.TOTP)


def double_auth_obligatoire(utilisateur):
    if not utilisateur.is_authenticated:
        return False
    if utilisateur.is_superuser:
        return True
    return bool(settings.DOUBLE_AUTH_ROLES) and a_le_role(utilisateur, *settings.DOUBLE_AUTH_ROLES)


def facteurs_actifs(utilisateur):
    """Types de seconds facteurs de l'utilisateur, ex. ["totp", "webauthn"] (jamais les secrets)."""
    if not utilisateur.is_authenticated:
        return []
    types = Authenticator.objects.filter(user_id=utilisateur.pk, type__in=SECONDS_FACTEURS).values_list("type", flat=True)
    return sorted(set(types))


def double_auth_active(utilisateur):
    """Vrai si l'utilisateur a au moins une clé de sécurité ou une application d'authentification."""
    return bool(facteurs_actifs(utilisateur))


def _chiffreur():
    """Chiffrement Fernet (AES + contrôle d'intégrité). Plusieurs clés : la première chiffre, toutes déchiffrent."""
    return MultiFernet([Fernet(cle) for cle in settings.MFA_CLES_CHIFFREMENT])


class AdaptateurDoubleAuth(DefaultMFAAdapter):
    """Réglages du module MFA d'allauth propres au socle (voir MFA_ADAPTER dans config/settings.py)."""

    def encrypt(self, text):
        # Par défaut, allauth stocke ces secrets en clair : quiconque lit la base pourrait générer les codes.
        return _chiffreur().encrypt(text.encode()).decode()

    def decrypt(self, encrypted_text):
        return _chiffreur().decrypt(encrypted_text.encode()).decode()

    def can_delete_authenticator(self, authenticator):
        """Interdit de retirer son dernier second facteur quand la double authentification est obligatoire."""
        utilisateur = authenticator.user
        if not double_auth_obligatoire(utilisateur):
            return True
        autres = Authenticator.objects.filter(user_id=utilisateur.pk, type__in=SECONDS_FACTEURS).exclude(pk=authenticator.pk)
        return autres.exists()
