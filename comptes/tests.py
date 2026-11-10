"""Tests des comptes, des rôles et des droits RGPD. Lancer : python manage.py test"""
import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from journal.models import EvenementAcces

from .roles import a_le_role, donne_role, role_requis, roles_de

Utilisateur = get_user_model()
MOT_DE_PASSE = "un-mot-de-passe-de-test-assez-long"


@override_settings(ROLES=["administrateur", "editrice", "client"])
class RolesTests(TestCase):
    def setUp(self):
        self.sophie = Utilisateur.objects.create_user("Sophie@Exemple.FR", MOT_DE_PASSE)

    def test_email_en_minuscules_et_mot_de_passe_hache(self):
        self.assertEqual(self.sophie.email, "sophie@exemple.fr")
        self.assertTrue(self.sophie.password.startswith("argon2"))

    def test_role_unique_et_roles_cumules(self):
        donne_role(self.sophie, "editrice")
        self.assertTrue(a_le_role(self.sophie, "editrice"))
        self.assertFalse(a_le_role(self.sophie, "administrateur"))
        donne_role(self.sophie, "client")
        self.assertEqual(sorted(roles_de(self.sophie)), ["client", "editrice"])

    def test_role_inconnu_refuse(self):
        with self.assertRaises(ValueError):
            a_le_role(self.sophie, "editirce")  # faute de frappe volontaire

    def test_compte_desactive_sans_role(self):
        donne_role(self.sophie, "editrice")
        self.sophie.is_active = False
        self.assertFalse(a_le_role(self.sophie, "editrice"))

    def test_decorateur_role_requis(self):
        vue = role_requis("editrice")(lambda request: HttpResponse("ok"))
        requete = RequestFactory().get("/")
        requete.user = self.sophie
        with self.assertRaises(PermissionDenied):
            vue(requete)
        donne_role(self.sophie, "editrice")
        self.assertEqual(vue(requete).status_code, 200)


@override_settings(ROLES=["administrateur", "client"])
class GroupesCreesTests(TestCase):
    def test_groupes_crees_apres_migrate(self):
        # Les tests partent d'une base migrée : les groupes des rôles par défaut doivent exister.
        from .roles import cree_groupes_des_roles

        cree_groupes_des_roles()
        self.assertTrue(Group.objects.filter(name="administrateur").exists())
        self.assertTrue(Group.objects.filter(name="client").exists())


class RgpdTests(TestCase):
    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user("client@exemple.fr", MOT_DE_PASSE)
        self.client.login(email="client@exemple.fr", password=MOT_DE_PASSE)

    def test_export_contient_compte_et_journal(self):
        reponse = self.client.get(reverse("comptes:export_donnees"))
        self.assertEqual(reponse.status_code, 200)
        self.assertIn("attachment", reponse["Content-Disposition"])
        donnees = json.loads(reponse.content)
        self.assertEqual(donnees["compte"]["email"], "client@exemple.fr")
        actions = [e["action"] for e in donnees["journal_acces"]]
        self.assertIn("connexion", actions)
        self.assertIn("export", actions)

    def test_suppression_refusee_sans_bon_mot_de_passe(self):
        self.client.post(reverse("comptes:supprimer_compte"), {"mot_de_passe": "faux"})
        self.assertTrue(Utilisateur.objects.filter(pk=self.utilisateur.pk).exists())

    def test_suppression_efface_le_compte_et_garde_une_trace_anonyme(self):
        pk = self.utilisateur.pk
        reponse = self.client.post(reverse("comptes:supprimer_compte"), {"mot_de_passe": MOT_DE_PASSE})
        self.assertRedirects(reponse, reverse("pages:accueil"))
        self.assertFalse(Utilisateur.objects.filter(pk=pk).exists())
        trace = EvenementAcces.objects.get(action="suppression", objet=f"compte:{pk}")
        self.assertIsNone(trace.utilisateur)

    def test_pages_du_compte_reservees_aux_connectes(self):
        self.client.logout()
        for nom in ("comptes:mes_donnees", "comptes:export_donnees", "comptes:supprimer_compte"):
            reponse = self.client.get(reverse(nom))
            self.assertEqual(reponse.status_code, 302, nom)
            self.assertIn(reverse("account_login"), reponse["Location"])
