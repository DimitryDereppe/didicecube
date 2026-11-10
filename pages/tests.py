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
