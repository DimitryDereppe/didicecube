"""Fonction à appeler dans les vues pour noter un accès dans le journal.

Exemple : journalise(request, "consultation", f"beneficiaire:{beneficiaire.pk}")
"""
from .models import EvenementAcces


def adresse_ip(request):
    """Adresse du visiteur. On ne lit pas X-Forwarded-For : un visiteur peut le falsifier.
    Derrière un proxy, c'est au proxy de transmettre la bonne adresse dans REMOTE_ADDR."""
    return request.META.get("REMOTE_ADDR") or None


def journalise(request, action, objet="", utilisateur=None, email_saisi=""):
    if action not in EvenementAcces.Action.values:
        raise ValueError(f"Action inconnue pour le journal : {action}")
    if utilisateur is None and request is not None and request.user.is_authenticated:
        utilisateur = request.user
    return EvenementAcces.objects.create(
        utilisateur=utilisateur,
        email_saisi=email_saisi[:254],
        action=action,
        objet=objet[:100],
        adresse_ip=adresse_ip(request) if request is not None else None,
    )
