from django.db import connection
from django.http import HttpResponse
from django.views.decorators.cache import never_cache


@never_cache
def sante(request):
    """Surveillance (Docker, sonde extérieure) : répond « ok » si l'application et la base répondent, sinon erreur 500."""
    with connection.cursor() as curseur:
        curseur.execute("SELECT 1")
    return HttpResponse("ok", content_type="text/plain")
