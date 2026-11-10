import math

from allauth.account.forms import LoginForm
from django import forms

from .limite_connexion import ATTRIBUT_ATTENTE


def message_attente(secondes):
    minutes = math.ceil(secondes / 60)
    duree = "1 minute" if minutes == 1 else f"{minutes} minutes"
    return f"Trop d'essais de connexion. Réessayez dans {duree}."


class ConnexionForm(LoginForm):
    """Formulaire de connexion d'allauth, qui affiche le temps d'attente quand les essais sont bloqués.

    Le blocage lui-même est fait par le moteur d'authentification (comptes/limite_connexion.py),
    qui note l'attente sur la requête. Le message est le même que le compte existe ou non.
    La page de connexion de l'admin renvoie vers celle-ci (config/urls.py) : une seule porte d'entrée.
    """

    def clean(self):
        try:
            return super().clean()
        except forms.ValidationError:
            attente = getattr(self.request, ATTRIBUT_ATTENTE, None)
            if attente:
                raise forms.ValidationError(message_attente(attente), code="trop_essais") from None
            raise


class ConfirmationSuppressionForm(forms.Form):
    """Demande le mot de passe avant de supprimer le compte, pour éviter une suppression par erreur ou par un tiers."""

    mot_de_passe = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))

    def __init__(self, utilisateur, *args, **kwargs):
        self.utilisateur = utilisateur
        super().__init__(*args, **kwargs)

    def clean_mot_de_passe(self):
        mot_de_passe = self.cleaned_data["mot_de_passe"]
        if not self.utilisateur.check_password(mot_de_passe):
            raise forms.ValidationError("Mot de passe incorrect.")
        return mot_de_passe
