import json
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.http import require_POST

from journal.outils import journalise

from . import moteur, resolution
from .forms import SkinForm, type_image
from .models import ImageSkin, Progression, Skin, valide_etat

COULEURS_AFFICHEES = {
    "B": {"nom": "blanc", "hex": "#ffffff"},
    "J": {"nom": "jaune", "hex": "#ffd500"},
    "R": {"nom": "rouge", "hex": "#c41e1e"},
    "O": {"nom": "orange", "hex": "#ff8c00"},
    "V": {"nom": "vert", "hex": "#009e26"},
    "L": {"nom": "bleu", "hex": "#0051ba"},
}


def _connexion_json(vue):
    """Comme login_required, mais répond en JSON (401) au lieu de rediriger : pour les appels du script."""
    @wraps(vue)
    def enveloppe(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"erreur": "Connectez-vous pour enregistrer votre progression."}, status=401)
        return vue(request, *args, **kwargs)
    return enveloppe


def _lit_json(request):
    try:
        donnees = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return None
    return donnees if isinstance(donnees, dict) else None


def _skins_de(utilisateur):
    if not utilisateur.is_authenticated:
        return []
    return [
        {
            "id": skin.id,
            "nom": skin.nom_skin,
            "images": {i.couleur: reverse("cube:image_skin", args=[i.id]) for i in skin.images.all()},
        }
        for skin in utilisateur.skins.prefetch_related("images")
    ]


def atelier(request):
    """Page principale : saisie du cube (à la main ou par photo), résolution et lecture pas à pas."""
    progression = None
    identifiant = request.GET.get("progression")
    if identifiant and request.user.is_authenticated and identifiant.isdigit():
        p = get_object_or_404(Progression, pk=identifiant, utilisateur=request.user)
        progression = {"id": p.id, "etat": p.etat_depart, "etape": p.etape_courante}
    donnees = {
        "mouvements": {nom: list(perm) for nom, perm in moteur.MOUVEMENTS.items()},
        "couleurs": COULEURS_AFFICHEES,
        "resolu": moteur.RESOLU,
        "progression": progression,
        "connecte": request.user.is_authenticated,
        "skins": _skins_de(request.user),
        "logo": static("img/izzu-tahutiz-marque.svg"),
        "urls": {
            "solution": reverse("cube:solution"),
            "enregistrer": reverse("cube:enregistrer"),
            "connexion": reverse("account_login") + "?next=" + reverse("cube:atelier"),
        },
    }
    return render(request, "cube/atelier.html", {"donnees": donnees})


@require_POST
def solution(request):
    """Calcule la solution d'un état (JSON {"etat": "54 lettres"}). Ouvert à tous, sans compte."""
    donnees = _lit_json(request)
    etat = donnees.get("etat") if donnees else None
    if not isinstance(etat, str):
        return JsonResponse({"erreur": "Requête mal formée."}, status=400)
    try:
        return JsonResponse(resolution.solution(etat))
    except resolution.EtatImpossible as erreur:
        return JsonResponse({"erreur": str(erreur)}, status=400)


@require_POST
@_connexion_json
def enregistrer(request):
    """Crée ou met à jour une progression : {"etat", "etape", "id" (facultatif)}."""
    donnees = _lit_json(request) or {}
    etat, etape, identifiant = donnees.get("etat"), donnees.get("etape", 0), donnees.get("id")
    try:
        valide_etat(etat if isinstance(etat, str) else "")
        if not isinstance(etape, int) or etape < 0:
            raise ValidationError("étape")
        resolution.verifie(etat)
    except (ValidationError, resolution.EtatImpossible):
        return JsonResponse({"erreur": "État du cube ou étape invalide."}, status=400)
    if identifiant is None:
        progression = Progression(utilisateur=request.user)
    elif isinstance(identifiant, int):
        progression = Progression.objects.filter(pk=identifiant, utilisateur=request.user).first()
        if progression is None:
            return JsonResponse({"erreur": "Progression introuvable."}, status=404)
    else:
        return JsonResponse({"erreur": "Requête mal formée."}, status=400)
    progression.etat_depart, progression.etape_courante = etat, etape
    progression.save()
    return JsonResponse({"id": progression.id})


@login_required
def progressions(request):
    return render(request, "cube/progressions.html", {"progressions": request.user.progressions.all()})


@login_required
@require_POST
def progression_supprimer(request, pk):
    get_object_or_404(Progression, pk=pk, utilisateur=request.user).delete()
    messages.success(request, "Progression supprimée.")
    return redirect("cube:progressions")


@login_required
def skins(request):
    form = SkinForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            skin = Skin.objects.create(utilisateur=request.user, nom_skin=form.cleaned_data["nom_skin"])
            for code, fichier in form.cleaned_data["images"].items():
                ImageSkin.objects.create(skin=skin, couleur=code, fichier=fichier)
        journalise(request, "creation", objet=f"skin:{skin.id}")
        messages.success(request, f"Skin « {skin.nom_skin} » ajouté.")
        return redirect("cube:skins")
    liste = request.user.skins.prefetch_related("images")
    return render(request, "cube/skins.html", {"form": form, "skins": liste})


@login_required
@require_POST
def skin_supprimer(request, pk):
    skin = get_object_or_404(Skin, pk=pk, utilisateur=request.user)
    nom = skin.nom_skin
    skin.delete()
    journalise(request, "suppression", objet=f"skin:{pk}")
    messages.success(request, f"Skin « {nom} » supprimé.")
    return redirect("cube:skins")


@login_required
def image_skin(request, pk):
    """Sert une image de skin à son propriétaire seulement (les images ne sont pas publiques)."""
    image = get_object_or_404(ImageSkin, pk=pk, skin__utilisateur=request.user)
    try:
        fichier = image.fichier.open("rb")
    except FileNotFoundError:
        raise Http404 from None
    mime = type_image(fichier.read(16)) or "application/octet-stream"
    fichier.seek(0)
    reponse = FileResponse(fichier, content_type=mime)
    reponse["Cache-Control"] = "private, max-age=86400"
    return reponse
