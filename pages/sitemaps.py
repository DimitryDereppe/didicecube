"""Plan du site (sitemap.xml) pour les moteurs de recherche : seulement les pages publiques."""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class PagesPubliques(Sitemap):
    changefreq = "monthly"

    def items(self):
        return ["pages:accueil", "cube:atelier", "pages:mentions_legales", "pages:confidentialite", "pages:accessibilite"]

    def location(self, nom):
        return reverse(nom)

    def priority(self, nom):
        return {"pages:accueil": 1.0, "cube:atelier": 0.9}.get(nom, 0.3)
