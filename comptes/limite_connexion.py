"""Limitation des tentatives de connexion par mot de passe (protection contre les essais en série).

Principe, pour chaque couple (email tapé, adresse IP) :
- les CONNEXION_ESSAIS_MAX premiers essais sont libres ;
- au dernier de ces essais, s'il échoue, le couple est bloqué CONNEXION_BLOCAGE_SECONDES ;
- chaque nouvel échec après un blocage double la durée, sans dépasser CONNEXION_BLOCAGE_MAX_SECONDES ;
- une connexion réussie remet le compteur à zéro ; sans essai pendant CONNEXION_OUBLI_SECONDES, il est oublié.

Le compteur ne dépend pas de l'existence du compte : un email inconnu est compté et bloqué de la même façon,
avec le même message. On ne peut donc pas s'en servir pour deviner quels comptes existent.

L'essai est compté AVANT de vérifier le mot de passe, sous verrou de ligne (select_for_update) :
des requêtes envoyées toutes en même temps ne peuvent pas dépasser la limite.

Le blocage passe par le moteur d'authentification (réglage AUTHENTICATION_BACKENDS) : il s'applique donc
à la page de connexion du site comme à celle de l'admin. Les formulaires de connexion (comptes/forms.py)
affichent ensuite le temps d'attente.
"""
import math
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import salted_hmac

from journal.outils import adresse_ip

from .models import TentativeConnexion

# Nom de l'attribut posé sur la requête quand l'essai est refusé : nombre de secondes à attendre.
ATTRIBUT_ATTENTE = "connexion_attente"


def _empreinte(email, ip):
    """Empreinte du couple (email, adresse IP) : impossible à relire sans SECRET_KEY, toujours 64 caractères."""
    valeur = f"{email.strip().lower()}|{ip or ''}"
    return salted_hmac("comptes.limite_connexion", valeur, algorithm="sha256").hexdigest()


def duree_blocage(echecs):
    """Durée du blocage (en secondes) après le nombre d'échecs donné ; 0 si on est encore sous la limite."""
    depassement = echecs - settings.CONNEXION_ESSAIS_MAX
    if depassement < 0:
        return 0
    # min(..., 30) évite de calculer des puissances de 2 démesurées : le plafond est atteint bien avant.
    return min(settings.CONNEXION_BLOCAGE_SECONDES * 2 ** min(depassement, 30), settings.CONNEXION_BLOCAGE_MAX_SECONDES)


def compte_essai(email, ip):
    """Compte un essai de connexion. Renvoie 0 si l'essai est permis, sinon le nombre de secondes à attendre.

    L'essai est compté d'avance comme un échec ; reussite() efface le compteur si le mot de passe était bon.
    """
    maintenant = timezone.now()
    with transaction.atomic():
        # Ménage : les compteurs trop anciens sont oubliés (ils contiennent une trace de l'adresse IP).
        TentativeConnexion.objects.filter(derniere__lt=maintenant - timedelta(seconds=settings.CONNEXION_OUBLI_SECONDES)).delete()
        # Verrou de ligne : deux essais simultanés sur le même couple passent l'un après l'autre.
        tentative, _ = TentativeConnexion.objects.select_for_update().get_or_create(
            cle=_empreinte(email, ip), defaults={"derniere": maintenant}
        )
        if tentative.bloque_jusqua and tentative.bloque_jusqua > maintenant:
            # Essai refusé sans être compté : attendre la fin du blocage suffit pour réessayer.
            return math.ceil((tentative.bloque_jusqua - maintenant).total_seconds())
        tentative.echecs += 1
        tentative.derniere = maintenant
        delai = duree_blocage(tentative.echecs)
        if delai:
            tentative.bloque_jusqua = maintenant + timedelta(seconds=delai)
        tentative.save()
    return 0


def reussite(email, ip):
    """Connexion réussie : le compteur du couple (email, adresse IP) est effacé."""
    TentativeConnexion.objects.filter(cle=_empreinte(email, ip)).delete()


class ModeleAvecLimiteBackend(ModelBackend):
    """Moteur d'authentification de Django (email + mot de passe), avec la limitation des essais en plus."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(get_user_model().USERNAME_FIELD)
        # Sans requête (ex. client.login() dans les tests, script interne), pas d'adresse IP : pas de limite.
        limite = request is not None and username and settings.CONNEXION_ESSAIS_MAX > 0
        if limite:
            attente = compte_essai(username, adresse_ip(request))
            if attente:
                setattr(request, ATTRIBUT_ATTENTE, attente)
                # PermissionDenied arrête la vérification : le mot de passe n'est même pas regardé.
                # Django envoie quand même le signal d'échec, noté au journal (journal/signaux.py).
                raise PermissionDenied
        utilisateur = super().authenticate(request, username=username, password=password, **kwargs)
        if limite and utilisateur is not None:
            reussite(username, adresse_ip(request))
        return utilisateur
