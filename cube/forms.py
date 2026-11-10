from django import forms

from .moteur import COULEURS

TAILLE_MAX = 2 * 1024 * 1024  # 2 Mo par image
# Signatures des formats acceptés (SVG refusé : il peut contenir du script).
FORMATS = {b"\x89PNG\r\n\x1a\n": "image/png", b"\xff\xd8\xff": "image/jpeg"}


def type_image(debut):
    """Type MIME d'après les premiers octets du fichier, ou None si le format n'est pas accepté."""
    for signature, mime in FORMATS.items():
        if debut.startswith(signature):
            return mime
    if debut[:4] == b"RIFF" and debut[8:12] == b"WEBP":
        return "image/webp"
    return None


class SkinForm(forms.Form):
    nom_skin = forms.CharField(label="Nom du skin", max_length=60)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for code, nom in COULEURS.items():
            self.fields[f"image_{code}"] = forms.FileField(
                label=f"Image pour le {nom}",
                required=False,
                help_text="PNG, JPEG ou WebP, 2 Mo au plus.",
                widget=forms.ClearableFileInput(attrs={"accept": "image/png,image/jpeg,image/webp"}),
            )

    def clean(self):
        donnees = super().clean()
        images = {}
        for code in COULEURS:
            fichier = donnees.get(f"image_{code}")
            if not fichier:
                continue
            if fichier.size > TAILLE_MAX:
                self.add_error(f"image_{code}", "Image trop lourde (2 Mo au plus).")
                continue
            debut = fichier.read(16)
            fichier.seek(0)
            if type_image(debut) is None:
                self.add_error(f"image_{code}", "Format non reconnu : PNG, JPEG ou WebP seulement.")
                continue
            images[code] = fichier
        if not images and not self.errors:
            raise forms.ValidationError("Ajoutez au moins une image.")
        donnees["images"] = images
        return donnees
