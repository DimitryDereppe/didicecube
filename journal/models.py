"""Journal d'accès : qui a fait quoi, quand, depuis quelle adresse.

Indispensable dès qu'on manipule des données sensibles (santé pour AppProject, finances pour le Cocon) :
le RGPD demande de pouvoir retrouver les accès. Le journal ne se modifie pas : on ajoute, on ne corrige pas.
"""
from django.conf import settings
from django.db import models


class EvenementAcces(models.Model):
    class Action(models.TextChoices):
        CONNEXION = "connexion", "Connexion"
        DECONNEXION = "deconnexion", "Déconnexion"
        ECHEC_CONNEXION = "echec_connexion", "Échec de connexion"
        CONSULTATION = "consultation", "Consultation"
        CREATION = "creation", "Création"
        MODIFICATION = "modification", "Modification"
        SUPPRESSION = "suppression", "Suppression"
        EXPORT = "export", "Export"
        DOUBLE_AUTH = "double_auth", "Double authentification"
        ECHEC_DOUBLE_AUTH = "echec_double_auth", "Échec de double authentification"

    # SET_NULL : si le compte est supprimé, l'événement reste mais n'est plus relié à la personne.
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="evenements_acces"
    )
    # Email tapé lors d'un échec de connexion (aucun compte connu dans ce cas). Effacé par la purge.
    email_saisi = models.CharField(max_length=254, blank=True)
    action = models.CharField(max_length=20, choices=Action.choices)
    # Ce qui a été touché, sous la forme "type:identifiant" (ex. "beneficiaire:12"). Jamais de contenu sensible.
    objet = models.CharField(max_length=100, blank=True)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "événement d'accès"
        verbose_name_plural = "journal d'accès"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date:%Y-%m-%d %H:%M} {self.get_action_display()} {self.objet}".strip()
