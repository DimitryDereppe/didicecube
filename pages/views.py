from django.db import connection
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.cache import never_cache


@never_cache
def sante(request):
    """Surveillance (Docker, sonde extérieure) : répond « ok » si l'application et la base répondent, sinon erreur 500."""
    with connection.cursor() as curseur:
        curseur.execute("SELECT 1")
    return HttpResponse("ok", content_type="text/plain")


def robots(request):
    """robots.txt : laisse les moteurs parcourir le site, sauf l'admin et les adresses techniques du cube."""
    lignes = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /cube/solution/",
        "Disallow: /cube/enregistrer/",
        "Disallow: /cube/skins/image/",
        "",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap'))}",
    ]
    return HttpResponse("\n".join(lignes) + "\n", content_type="text/plain")
