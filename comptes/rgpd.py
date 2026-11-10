"""Droits RGPD de l'utilisateur : export de ses données (art. 15 et 20) et suppression du compte (art. 17).

Le socle exporte le compte, les rôles et le journal d'accès. Chaque projet ajoute ses propres
données grâce à settings.EXPORT_DONNEES_FONCTIONS (voir config/settings.py).
"""
from django.conf import settings
from django.utils import timezone
from django.utils.module_loading import import_string

from journal.models import EvenementAcces

from .double_auth import facteurs_actifs
from .roles import roles_de


def donnees_du_socle(utilisateur):
    return {
        "compte": {
            "email": utilisateur.email,
            "prenom": utilisateur.first_name,
            "nom": utilisateur.last_name,
            "inscrit_le": utilisateur.date_joined.isoformat(),
            "derniere_connexion": utilisateur.last_login.isoformat() if utilisateur.last_login else None,
            "roles": roles_de(utilisateur),
            # Jamais les secrets ni les codes de secours : seulement l'état et le type des facteurs.
            "double_authentification_active": bool(facteurs_actifs(utilisateur)),
            "seconds_facteurs": facteurs_actifs(utilisateur),
        },
        "journal_acces": [
            {"date": e.date.isoformat(), "action": e.action, "objet": e.objet, "adresse_ip": e.adresse_ip}
            for e in EvenementAcces.objects.filter(utilisateur=utilisateur).order_by("date")
        ],
    }


def exporte_donnees(utilisateur):
    """Rassemble toutes les données de l'utilisateur dans un dictionnaire (converti en JSON par la vue)."""
    donnees = {"exporte_le": timezone.now().isoformat(), "site": settings.SITE_NOM}
    donnees.update(donnees_du_socle(utilisateur))
    for chemin in settings.EXPORT_DONNEES_FONCTIONS:
        donnees.update(import_string(chemin)(utilisateur))
    return donnees
