"""Aides pour les tests des projets : comptes avec double authentification.

Exemples :
    connecte_avec_double_auth(self.client, admin)   # session connectée, facteur déjà en place
    totp = active_application(utilisateur)           # application d'authentification
    code_actuel(totp)                                # le code que le téléphone afficherait
"""
import time

from allauth.account.internal.flows.login import (
    _AUTHENTICATION_METHODS_USER_SESSION_KEY,
    AUTHENTICATION_METHODS_SESSION_KEY,
)
from allauth.mfa.models import Authenticator
from allauth.mfa.totp.internal.auth import TOTP, format_hotp_value, generate_totp_secret, hotp_value
from allauth.mfa.utils import decrypt


def active_application(utilisateur):
    """Ajoute une application d'authentification (TOTP) à l'utilisateur et la renvoie."""
    return TOTP.activate(utilisateur, generate_totp_secret()).instance


def code_actuel(authenticator):
    """Code à 6 chiffres que l'application du téléphone afficherait en ce moment."""
    secret = decrypt(authenticator.data["secret"])
    return format_hotp_value(hotp_value(secret, int(time.time()) // 30))


def connecte_avec_double_auth(client, utilisateur):
    """Connecte l'utilisateur comme s'il avait passé mot de passe et second facteur (crée une application si besoin).

    La session note aussi un mot de passe retapé à l'instant : allauth l'exige avant d'ajouter ou de retirer un facteur.
    """
    authenticator = Authenticator.objects.filter(user_id=utilisateur.pk, type=Authenticator.Type.TOTP).first()
    if authenticator is None:
        authenticator = active_application(utilisateur)
    client.force_login(utilisateur)
    session = client.session
    session[_AUTHENTICATION_METHODS_USER_SESSION_KEY] = str(utilisateur.pk)
    session[AUTHENTICATION_METHODS_SESSION_KEY] = [{"method": "password", "at": time.time(), "reauthenticated": True}]
    session.save()
    return authenticator
