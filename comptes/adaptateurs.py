"""Réglages de django-allauth propres au socle (voir ACCOUNT_ADAPTER dans config/settings.py)."""
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class AdaptateurComptes(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """Inscription libre seulement si le projet l'ouvre (INSCRIPTION_OUVERTE=true dans .env)."""
        return settings.INSCRIPTION_OUVERTE

    def pre_authenticate(self, request, **credentials):
        """Pas de second limiteur sur le mot de passe : comptes/limite_connexion.py s'en charge.

        Celui d'allauth compte les échecs par email seul : 5 mots de passe faux tapés par n'importe qui
        bloqueraient le vrai titulaire du compte. Le nôtre compte par couple (email, adresse IP), en base.
        Le limiteur d'allauth reste actif pour les codes de double authentification.
        """
        self._login_failed_rl_usage = None
