"""Tests de la limitation des tentatives de connexion (comptes/limite_connexion.py)."""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from journal.models import EvenementAcces

from .limite_connexion import duree_blocage
from .models import TentativeConnexion

MOT_DE_PASSE = "un-mot-de-passe-de-test-assez-long"
EMAIL = "sophie@exemple.fr"


@override_settings(
    CONNEXION_ESSAIS_MAX=5,
    CONNEXION_BLOCAGE_SECONDES=60,
    CONNEXION_BLOCAGE_MAX_SECONDES=3600,
    CONNEXION_OUBLI_SECONDES=86400,
)
class LimiteConnexionTests(TestCase):
    def setUp(self):
        cache.clear()  # limites d'allauth (30 connexions par minute et par IP) : repartir de zéro
        get_user_model().objects.create_user(EMAIL, MOT_DE_PASSE)

    def essai(self, email=EMAIL, mot_de_passe="faux", ip="127.0.0.1", url="account_login"):
        """Envoie le formulaire de connexion et renvoie les erreurs affichées (liste de textes)."""
        reponse = self.client.post(reverse(url), {"login": email, "password": mot_de_passe}, REMOTE_ADDR=ip)
        if reponse.status_code == 302:
            return []
        return list(reponse.context["form"].non_field_errors())

    def fin_du_blocage(self):
        """Fait comme si le temps de blocage était écoulé."""
        TentativeConnexion.objects.update(bloque_jusqua=timezone.now() - timedelta(seconds=1))

    def test_bloque_apres_cinq_echecs_meme_avec_le_bon_mot_de_passe(self):
        for _ in range(5):
            self.assertNotIn("Trop d'essais", " ".join(self.essai()))
        erreurs = self.essai(mot_de_passe=MOT_DE_PASSE)
        self.assertEqual(erreurs, ["Trop d'essais de connexion. Réessayez dans 1 minute."])
        self.assertNotIn("_auth_user_id", self.client.session)
        # L'essai refusé est noté au journal, marqué « blocage ».
        self.assertEqual(EvenementAcces.objects.filter(action="echec_connexion", objet="blocage").count(), 1)
        self.assertEqual(EvenementAcces.objects.filter(action="echec_connexion", objet="").count(), 5)

    def test_meme_message_que_le_compte_existe_ou_non(self):
        messages_compte_connu = [self.essai() for _ in range(6)]
        messages_compte_inconnu = [self.essai(email="personne@exemple.fr") for _ in range(6)]
        self.assertEqual(messages_compte_connu, messages_compte_inconnu)
        self.assertIn("Trop d'essais", messages_compte_inconnu[-1][0])

    def test_blocage_qui_double_puis_plafonne(self):
        for _ in range(5):
            self.essai()
        attendus = [120, 240, 480, 960, 1920, 3600, 3600]
        for attendu in attendus:
            self.fin_du_blocage()
            avant = timezone.now()
            self.essai()
            tentative = TentativeConnexion.objects.get()
            self.assertAlmostEqual((tentative.bloque_jusqua - avant).total_seconds(), attendu, delta=5)
        self.assertEqual(self.essai(), ["Trop d'essais de connexion. Réessayez dans 60 minutes."])

    def test_connexion_reussie_remet_le_compteur_a_zero(self):
        for _ in range(4):
            self.essai()
        self.assertEqual(self.essai(mot_de_passe=MOT_DE_PASSE), [])
        self.assertFalse(TentativeConnexion.objects.exists())

    def test_autre_adresse_ip_non_bloquee(self):
        for _ in range(6):
            self.essai()
        self.assertEqual(self.essai(mot_de_passe=MOT_DE_PASSE, ip="10.0.0.2"), [])

    def test_compteur_oublie_apres_le_delai(self):
        for _ in range(5):
            self.essai()
        TentativeConnexion.objects.update(
            derniere=timezone.now() - timedelta(days=2), bloque_jusqua=timezone.now() + timedelta(hours=1)
        )
        self.assertEqual(self.essai(mot_de_passe=MOT_DE_PASSE), [])

    def test_ni_email_ni_adresse_en_clair(self):
        self.essai()
        tentative = TentativeConnexion.objects.get()
        self.assertEqual(len(tentative.cle), 64)
        self.assertNotIn("sophie", tentative.cle)
        self.assertNotIn("127", tentative.cle)

    def test_majuscules_comptees_avec_les_minuscules(self):
        for _ in range(5):
            self.essai(email="Sophie@Exemple.fr")
        self.assertIn("Trop d'essais", self.essai()[0])

    def test_page_de_connexion_de_l_admin_renvoie_vers_celle_du_site(self):
        # Une seule porte d'entrée, avec la limitation et la double authentification.
        reponse = self.client.get(reverse("admin:login"))
        self.assertEqual(reponse.status_code, 302)
        self.assertTrue(reponse["Location"].startswith(reverse("account_login")))

    @override_settings(CONNEXION_ESSAIS_MAX=0)
    def test_limite_desactivee_avec_zero(self):
        for _ in range(10):
            self.essai()
        self.assertEqual(self.essai(mot_de_passe=MOT_DE_PASSE), [])
        self.assertFalse(TentativeConnexion.objects.exists())

    def test_duree_blocage(self):
        self.assertEqual([duree_blocage(n) for n in (0, 4, 5, 6, 7, 100)], [0, 0, 60, 120, 240, 3600])
