"""Progressions sauvegardées et skins (habillages) des utilisateurs. Voir docs/conception/06-dictionnaire-de-donnees.md."""
import uuid
from pathlib import Path

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from .moteur import COULEURS

valide_etat = RegexValidator(r"^[BJROVL]{54}$", "54 lettres parmi B, J, R, O, V, L.")


class Progression(models.Model):
    """État de départ d'un cube et étape atteinte. La solution n'est pas stockée : elle se recalcule."""

    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progressions")
    etat_depart = models.CharField("état de départ", max_length=54, validators=[valide_etat])
    etape_courante = models.PositiveIntegerField("mouvement atteint", default=0)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_maj = models.DateTimeField("dernière sauvegarde", auto_now=True)

    class Meta:
        ordering = ["-date_maj"]

    def __str__(self):
        return f"Progression du {self.date_maj:%d/%m/%Y %H:%M}"


class Skin(models.Model):
    """Habillage du cube : une image (facultative) par couleur standard."""

    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="skins")
    nom_skin = models.CharField("nom du skin", max_length=60)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nom_skin"]

    def __str__(self):
        return self.nom_skin


def _chemin_image(instance, nom_fichier):
    # Nom aléatoire : le nom d'origine (parfois personnel) n'est ni gardé ni deviné.
    return f"skins/{uuid.uuid4().hex}{Path(nom_fichier).suffix.lower()}"


class ImageSkin(models.Model):
    skin = models.ForeignKey(Skin, on_delete=models.CASCADE, related_name="images")
    couleur = models.CharField(max_length=1, choices=list(COULEURS.items()))
    fichier = models.FileField(upload_to=_chemin_image)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["skin", "couleur"], name="une_image_par_couleur")]

    def __str__(self):
        return f"{self.skin} : {self.get_couleur_display()}"
