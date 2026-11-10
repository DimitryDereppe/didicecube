"""Rend le nom du site disponible dans tous les gabarits : {{ SITE_NOM }} et {{ INSCRIPTION_OUVERTE }}."""
from django.conf import settings


def site(request):
    return {"SITE_NOM": settings.SITE_NOM, "INSCRIPTION_OUVERTE": settings.INSCRIPTION_OUVERTE}
