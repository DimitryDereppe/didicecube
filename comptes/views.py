import json

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET

from journal.outils import journalise

from .double_auth import double_auth_obligatoire, facteurs_actifs
from .forms import ConfirmationSuppressionForm
from .rgpd import exporte_donnees


@login_required
def mes_donnees(request):
    """Page « Mon compte » : mot de passe, double authentification, téléchargement et suppression des données.

    La double authentification elle-même se gère sur les pages d'allauth (adresse « mfa_index »).
    """
    facteurs = facteurs_actifs(request.user)
    contexte = {
        "double_auth_active": bool(facteurs),
        "double_auth_obligatoire": double_auth_obligatoire(request.user),
        "cle_securite": "webauthn" in facteurs,
        "application": "totp" in facteurs,
    }
    return render(request, "comptes/mes_donnees.html", contexte)


@login_required
@require_GET
def export_donnees(request):
    """Télécharge toutes les données de l'utilisateur au format JSON."""
    journalise(request, "export", f"compte:{request.user.pk}")
    contenu = json.dumps(exporte_donnees(request.user), ensure_ascii=False, indent=2)
    reponse = HttpResponse(contenu, content_type="application/json; charset=utf-8")
    nom = f"mes-donnees-{timezone.localdate().isoformat()}.json"
    reponse["Content-Disposition"] = f'attachment; filename="{nom}"'
    return reponse


@login_required
def supprimer_compte(request):
    """Supprime le compte après confirmation par mot de passe.

    Le journal d'accès garde la trace de la suppression, sans lien vers la personne
    (la clé étrangère passe à vide) : on sait qu'un compte a été supprimé, pas par qui.
    """
    form = ConfirmationSuppressionForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        utilisateur = request.user
        journalise(request, "suppression", f"compte:{utilisateur.pk}")
        logout(request)
        utilisateur.delete()
        messages.success(request, "Votre compte et vos données ont été supprimés.")
        return redirect("pages:accueil")
    return render(request, "comptes/supprimer_compte.html", {"form": form})
