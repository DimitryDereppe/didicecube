"""Modèle utilisateur du socle : on se connecte avec son adresse email (pas de nom d'utilisateur).

Le modèle est personnalisé dès le départ, comme le recommande Django : le changer plus tard,
une fois la base remplie, est très difficile.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class GestionnaireUtilisateurs(BaseUserManager):
    """Crée les comptes à partir d'un email (en minuscules) et d'un mot de passe."""

    use_in_migrations = True

    def _cree(self, email, password, **champs):
        if not email:
            raise ValueError("L'adresse email est obligatoire.")
        utilisateur = self.model(email=self.normalize_email(email).lower(), **champs)
        utilisateur.set_password(password)  # le mot de passe est haché (argon2), jamais stocké en clair
        utilisateur.save(using=self._db)
        return utilisateur

    def create_user(self, email, password=None, **champs):
        champs.setdefault("is_staff", False)
        champs.setdefault("is_superuser", False)
        return self._cree(email, password, **champs)

    def create_superuser(self, email, password=None, **champs):
        champs["is_staff"] = True
        champs["is_superuser"] = True
        return self._cree(email, password, **champs)


class Utilisateur(AbstractUser):
    username = None  # on retire le nom d'utilisateur de Django
    email = models.EmailField("adresse email", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # createsuperuser ne demande que l'email et le mot de passe

    objects = GestionnaireUtilisateurs()

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"

    def __str__(self):
        return self.email


class TentativeConnexion(models.Model):
    """Compteur d'échecs de connexion pour un couple (email tapé, adresse IP). Voir comptes/limite_connexion.py.

    On ne garde ni l'email ni l'adresse en clair : seulement une empreinte (HMAC avec SECRET_KEY).
    La ligne disparaît après une connexion réussie, ou quand elle est oubliée (CONNEXION_OUBLI_SECONDES).
    """

    cle = models.CharField(max_length=64, unique=True)
    echecs = models.PositiveIntegerField(default=0)
    bloque_jusqua = models.DateTimeField(null=True, blank=True)
    derniere = models.DateTimeField(db_index=True)

    class Meta:
        verbose_name = "tentative de connexion"
        verbose_name_plural = "tentatives de connexion"

    def __str__(self):
        # Empreinte tronquée : l'email et l'adresse IP ne sont pas stockés en clair.
        return f"{self.cle[:12]}… : {self.echecs} échec(s)"
