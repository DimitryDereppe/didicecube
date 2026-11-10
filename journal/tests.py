from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from comptes.outils_tests import connecte_avec_double_auth

from .models import EvenementAcces

MOT_DE_PASSE = "un-mot-de-passe-de-test-assez-long"


class JournalTests(TestCase):
    def setUp(self):
        cache.clear()  # limites d'allauth, partagées entre les tests
        self.utilisateur = get_user_model().objects.create_user("a@exemple.fr", MOT_DE_PASSE)

    def test_connexion_deconnexion_et_echec_journalises(self):
        self.client.post(reverse("account_login"), {"login": "a@exemple.fr", "password": "faux"})
        self.client.post(reverse("account_login"), {"login": "a@exemple.fr", "password": MOT_DE_PASSE})
        self.client.post(reverse("account_logout"))
        actions = list(EvenementAcces.objects.order_by("date", "pk").values_list("action", flat=True))
        self.assertEqual(actions, ["echec_connexion", "connexion", "deconnexion"])
        echec = EvenementAcces.objects.get(action="echec_connexion")
        self.assertEqual(echec.email_saisi, "a@exemple.fr")
        self.assertEqual(echec.adresse_ip, "127.0.0.1")

    def test_purge_efface_seulement_les_vieux_evenements(self):
        vieux = EvenementAcces.objects.create(action="connexion", utilisateur=self.utilisateur)
        EvenementAcces.objects.filter(pk=vieux.pk).update(date=timezone.now() - timedelta(days=400))
        recent = EvenementAcces.objects.create(action="connexion", utilisateur=self.utilisateur)
        call_command("purge_journal", "--jours", "365", stdout=open("/dev/null", "w"))
        self.assertFalse(EvenementAcces.objects.filter(pk=vieux.pk).exists())
        self.assertTrue(EvenementAcces.objects.filter(pk=recent.pk).exists())

    def test_admin_en_lecture_seule(self):
        admin = get_user_model().objects.create_superuser("admin@exemple.fr", MOT_DE_PASSE)
        connecte_avec_double_auth(self.client, admin)  # l'admin exige la double authentification
        evenement = EvenementAcces.objects.create(action="connexion")
        self.assertEqual(self.client.get(reverse("admin:journal_evenementacces_changelist")).status_code, 200)
        self.assertEqual(self.client.get(reverse("admin:journal_evenementacces_add")).status_code, 403)
        self.assertEqual(self.client.post(reverse("admin:journal_evenementacces_delete", args=[evenement.pk])).status_code, 403)
