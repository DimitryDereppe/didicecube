"""Oblige à activer la double authentification quand elle est obligatoire (admin compris).

La vérification du second facteur à la connexion est faite par allauth : tant que le code (ou la clé)
n'est pas validé, la personne n'est pas connectée du tout. Ce middleware ne s'occupe donc que d'un cas :
la double authentification est obligatoire pour l'utilisateur mais il n'a encore aucun second facteur.
Il est alors renvoyé vers la page « Double authentification » ; seules cette page (et ses sous-pages),
la confirmation du mot de passe, la déconnexion et les fichiers statiques restent accessibles.
"""
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from .double_auth import double_auth_active, double_auth_obligatoire


class DoubleAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        utilisateur = request.user
        if (
            utilisateur.is_authenticated
            and not self._chemin_libre(request.path)
            and double_auth_obligatoire(utilisateur)
            and not double_auth_active(utilisateur)
        ):
            messages.warning(
                request,
                "La double authentification est obligatoire pour votre compte. "
                "Ajoutez une clé de sécurité (conseillé) ou une application d'authentification.",
            )
            return redirect("mfa_index")
        return self.get_response(request)

    @staticmethod
    def _chemin_libre(chemin):
        # Toutes les pages de la double authentification sont sous la même adresse (ex. /compte/2fa/…).
        if chemin.startswith(reverse("mfa_index")):
            return True
        libres = (reverse("account_logout"), reverse("account_reauthenticate"))
        return chemin in libres or chemin.startswith("/" + settings.STATIC_URL.lstrip("/"))
