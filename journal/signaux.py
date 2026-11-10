"""Enregistre automatiquement connexions, déconnexions, échecs et événements de double authentification."""
from allauth.mfa import signals as mfa
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .outils import journalise


@receiver(user_logged_in)
def connexion(sender, request, user, **kwargs):
    journalise(request, "connexion", utilisateur=user)


@receiver(user_logged_out)
def deconnexion(sender, request, user, **kwargs):
    if user is not None:
        journalise(request, "deconnexion", utilisateur=user)


@receiver(user_login_failed)
def echec_connexion(sender, credentials, request=None, **kwargs):
    # Essai refusé d'office (trop d'essais, voir comptes/limite_connexion.py) : objet « blocage ».
    objet = "blocage" if getattr(request, "connexion_attente", None) else ""
    email = credentials.get("username", "") or credentials.get("email", "")
    journalise(request, "echec_connexion", objet, email_saisi=email)


# --- Double authentification (signaux du module MFA d'allauth) ---------------------------------
# Objet noté : "<événement>:<type de facteur>", ex. "activation:webauthn". Jamais de secret.


@receiver(mfa.authenticator_added)
def facteur_ajoute(sender, request, user, authenticator, **kwargs):
    journalise(request, "double_auth", f"activation:{authenticator.type}", utilisateur=user)


@receiver(mfa.authenticator_removed)
def facteur_retire(sender, request, user, authenticator, **kwargs):
    journalise(request, "double_auth", f"retrait:{authenticator.type}", utilisateur=user)


@receiver(mfa.authenticator_reset)
def facteur_renouvele(sender, request, user, authenticator, **kwargs):
    journalise(request, "double_auth", f"renouvellement:{authenticator.type}", utilisateur=user)


@receiver(mfa.authenticator_used)
def facteur_utilise(sender, request, user, authenticator, **kwargs):
    journalise(request, "double_auth", f"verification:{authenticator.type}", utilisateur=user)


@receiver(mfa.authentication_failed)
def facteur_refuse(sender, request, user, **kwargs):
    authenticator = kwargs.get("authenticator")
    objet = f"compte:{user.pk}" if authenticator is None else f"{authenticator.type}:compte:{user.pk}"
    journalise(request, "echec_double_auth", objet, utilisateur=user)
