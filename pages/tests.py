from django.test import TestCase
from django.urls import reverse


class PagesTests(TestCase):
    def test_pages_publiques(self):
        pages = ("pages:accueil", "pages:mentions_legales", "pages:confidentialite", "pages:accessibilite")
        pages += ("account_login", "account_reset_password")
        for nom in pages:
            reponse = self.client.get(reverse(nom))
            self.assertEqual(reponse.status_code, 200, nom)
            self.assertContains(reponse, '<html lang="fr">')

    def test_onglet_accessibilite(self):
        reponse = self.client.get(reverse("pages:accueil"))
        self.assertContains(reponse, "js/accessibilite.js")
        self.assertContains(reponse, f'data-declaration="{reverse("pages:accessibilite")}"')

    def test_en_tetes_de_securite(self):
        reponse = self.client.get(reverse("pages:accueil"))
        self.assertEqual(reponse["X-Frame-Options"], "DENY")
        self.assertEqual(reponse["X-Content-Type-Options"], "nosniff")

    def test_sante(self):
        reponse = self.client.get(reverse("pages:sante"))
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.content, b"ok")
        self.assertIn("no-cache", reponse["Cache-Control"])

    def test_referencement_page_publique(self):
        reponse = self.client.get(reverse("pages:accueil"))
        self.assertContains(reponse, '<meta name="description"')
        self.assertContains(reponse, '<meta name="robots" content="index, follow">')
        self.assertContains(reponse, '<link rel="canonical" href="http://testserver/">')
        self.assertContains(reponse, '"@type": "WebApplication"')

    def test_pages_privees_hors_index(self):
        for nom in ("account_login", "account_reset_password"):
            self.assertContains(self.client.get(reverse(nom)), '<meta name="robots" content="noindex, nofollow">')

    def test_robots_txt(self):
        reponse = self.client.get("/robots.txt")
        self.assertEqual(reponse["Content-Type"], "text/plain")
        self.assertContains(reponse, "Disallow: /admin/")
        self.assertContains(reponse, "Sitemap: http://testserver/sitemap.xml")

    def test_sitemap(self):
        reponse = self.client.get("/sitemap.xml")
        self.assertEqual(reponse.status_code, 200)
        self.assertContains(reponse, "<loc>http://testserver/</loc>")
        self.assertContains(reponse, f"<loc>http://testserver{reverse('cube:atelier')}</loc>")
        self.assertNotContains(reponse, "progressions")
