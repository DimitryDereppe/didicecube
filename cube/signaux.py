"""Efface le fichier d'une image de skin quand elle est supprimée (y compris avec le compte)."""
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import ImageSkin


@receiver(post_delete, sender=ImageSkin)
def efface_fichier(sender, instance, **kwargs):
    instance.fichier.delete(save=False)
