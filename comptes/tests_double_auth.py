"""Tests de la double authentification (module MFA de django-allauth). Lancer : python manage.py test"""
import time

from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
from allauth.mfa.totp.internal.auth import SECRET_SESSION_KEY, format_hotp_value, hotp_value
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from journal.models import EvenementAcces

from .checks import roles_double_auth
from .double_auth import AdaptateurDoubleAuth
from .outils_tests import active_application, code_actuel, connecte_avec_double_auth
from .roles import donne_role

Utilisateur = get_user_model()
MOT_DE_PASSE = "un-mot-de-passe-de-test-assez-long"
ROLES_TEST = {"ROLES": ["administrateur", "editrice", "client"], "DOUBLE_AUTH_ROLES": ["administrateur", "editrice"]}


def connecte_avec_mot_de_passe(client, email):
    """Première étape de la connexion : email et mot de passe. Renvoie la réponse."""
    return client.post(reverse("account_login"), {"login": email, "password": MOT_DE_PASSE})


@override_settings(**ROLES_TEST)
class ObligationTests(TestCase):
    def test_role_obligatoire_renvoye_vers_la_double_auth(self):
        sophie = Utilisateur.objects.create_user("sophie@exemple.fr", MOT_DE_PASSE)
        donne_role(sophie, "editrice")
        self.client.force_login(sophie)
        reponse = self.client.get(reverse("comptes:mes_donnees"))
        self.assertRedirects(reponse, reverse("mfa_index"))
        # La page de la double authentification, elle, reste accessible.
        self.assertEqual(self.client.get(reverse("mfa_index")).status_code, 200)

    def test_superutilisateur_bloque_aussi_dans_l_admin(self):
        admin = Utilisateur.objects.create_superuser("admin@exemple.fr", MOT_DE_PASSE)
        self.client.force_login(admin)
        reponse = self.client.get("/admin/")
        self.assertRedirects(reponse, reverse("mfa_index"))

    def test_role_non_concerne_navigue_librement(self):
        client = Utilisateur.objects.create_user("client@exemple.fr", MOT_DE_PASSE)
        donne_role(client, "client")
        self.client.force_login(client)
        self.assertEqual(self.client.get(reverse("comptes:mes_donnees")).status_code, 200)

    def test_codes_de_secours_seuls_ne_suffisent_pas(self):
        sophie = Utilisateur.objects.create_user("sophie@exemple.fr", MOT_DE_PASSE)
        donne_role(sophie, "editrice")
        RecoveryCodes.activate(sophie)
        self.client.force_login(sophie)
        self.assertRedirects(self.client.get(reverse("comptes:mes_donnees")), reverse("mfa_index"))

    def test_erreur_si_role_inconnu(self):
        with self.settings(DOUBLE_AUTH_ROLES=["editirce"]):
            erreurs = roles_double_auth(None)
        self.assertEqual([e.id for e in erreurs], ["comptes.E001"])
        self.assertEqual(roles_double_auth(None), [])


@override_settings(**ROLES_TEST)
class ActivationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.sophie = Utilisateur.objects.create_user("sophie@exemple.fr", MOT_DE_PASSE)
        donne_role(self.sophie, "editrice")
        connecte_avec_mot_de_passe(self.client, "sophie@exemple.fr")
        # allauth demande de retaper le mot de passe (moins de 5 minutes avant) pour ajouter ou retirer un facteur.
        self.client.post(reverse("account_reauthenticate"), {"password": MOT_DE_PASSE})

    def test_mot_de_passe_redemande_avant_d_ajouter_un_facteur(self):
        self.client.post(reverse("account_logout"))
        connecte_avec_mot_de_passe(self.client, "sophie@exemple.fr")
        reponse = self.client.get(reverse("mfa_activate_totp"))
        self.assertTrue(reponse["Location"].startswith(reverse("account_reauthenticate")))

    def test_activation_de_l_application_avec_un_vrai_code(self):
        url = reverse("mfa_activate_totp")
        page = self.client.get(url)
        self.assertContains(page, "data:image/svg+xml")  # QR code intégré à la page (aucun service extérieur)
        secret = self.client.session[SECRET_SESSION_KEY]
        code = format_hotp_value(hotp_value(secret, int(time.time()) // 30))
        # allauth envoie le signal « facteur ajouté » après validation de la transaction : on l'exécute ici.
        with self.captureOnCommitCallbacks(execute=True):
            self.client.post(url, {"code": code})

        totp = Authenticator.objects.get(user=self.sophie, type=Authenticator.Type.TOTP)
        # Le secret est chiffré en base : on ne le retrouve pas en clair.
        self.assertNotIn(secret, str(totp.data))
        self.assertEqual(AdaptateurDoubleAuth().decrypt(totp.data["secret"]), secret)
        # Les codes de secours sont créés en même temps, et leur graine est chiffrée aussi.
        self.assertTrue(Authenticator.objects.filter(user=self.sophie, type=Authenticator.Type.RECOVERY_CODES).exists())
        self.assertTrue(EvenementAcces.objects.filter(action="double_auth", objet="activation:totp").exists())
        # La double authentification est en place : le compte est accessible.
        self.assertEqual(self.client.get(reverse("comptes:mes_donnees")).status_code, 200)

    def test_code_faux_refuse(self):
        url = reverse("mfa_activate_totp")
        self.client.get(url)
        self.client.post(url, {"code": "000000"})
        self.assertFalse(Authenticator.objects.filter(user=self.sophie, type=Authenticator.Type.TOTP).exists())

    def test_page_cle_de_securite_disponible(self):
        page = self.client.get(reverse("mfa_add_webauthn"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "webauthn.js")


@override_settings(**ROLES_TEST)
class VerificationTests(TestCase):
    def setUp(self):
        cache.clear()  # le limiteur d'allauth et l'anti-rejeu des codes utilisent le cache
        self.sophie = Utilisateur.objects.create_user("sophie@exemple.fr", MOT_DE_PASSE)
        donne_role(self.sophie, "editrice")
        self.totp = active_application(self.sophie)

    def test_code_demande_apres_le_mot_de_passe(self):
        reponse = connecte_avec_mot_de_passe(self.client, "sophie@exemple.fr")
        self.assertRedirects(reponse, reverse("mfa_authenticate"), fetch_redirect_response=False)
        # Tant que le code n'est pas donné, la personne n'est pas connectée.
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_bon_code_connecte_et_journalise(self):
        connecte_avec_mot_de_passe(self.client, "sophie@exemple.fr")
        self.client.post(reverse("mfa_authenticate"), {"code": code_actuel(self.totp)})
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.sophie.pk)
        self.assertTrue(EvenementAcces.objects.filter(action="double_auth", objet="verification:totp").exists())
        self.assertTrue(EvenementAcces.objects.filter(action="connexion", utilisateur=self.sophie).exists())

    def test_code_faux_journalise_puis_freinage(self):
        connecte_avec_mot_de_passe(self.client, "sophie@exemple.fr")
        url = reverse("mfa_authenticate")
        for _ in range(5):
            self.client.post(url, {"code": "000000"})
        self.assertEqual(EvenementAcces.objects.filter(action="echec_double_auth").count(), 5)
        # Après 5 codes faux, même le bon code est refusé un moment (freinage des essais en série).
        self.client.post(url, {"code": code_actuel(self.totp)})
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_redirection_vers_un_autre_site_refusee(self):
        self.client.post(
            reverse("account_login"), {"login": "sophie@exemple.fr", "password": MOT_DE_PASSE, "next": "https://piege.example/"}
        )
        reponse = self.client.post(reverse("mfa_authenticate"), {"code": code_actuel(self.totp)})
        self.assertEqual(reponse.status_code, 302)
        self.assertFalse(reponse["Location"].startswith("https://piege.example"))

    def test_code_de_secours_a_usage_unique(self):
        codes = RecoveryCodes.activate(self.sophie).generate_codes()
        connecte_avec_mot_de_passe(self.client, "sophie@exemple.fr")
        self.client.post(reverse("mfa_authenticate"), {"code": codes[0]})
        self.assertIn("_auth_user_id", self.client.session)
        # Nouvelle connexion : le même code de secours ne marche plus.
        self.client.post(reverse("account_logout"))
        connecte_avec_mot_de_passe(self.client, "sophie@exemple.fr")
        self.client.post(reverse("mfa_authenticate"), {"code": codes[0]})
        self.assertNotIn("_auth_user_id", self.client.session)


@override_settings(**ROLES_TEST)
class DesactivationTests(TestCase):
    def test_refusee_si_obligatoire_et_dernier_facteur(self):
        sophie = Utilisateur.objects.create_user("sophie@exemple.fr", MOT_DE_PASSE)
        donne_role(sophie, "editrice")
        connecte_avec_double_auth(self.client, sophie)
        self.client.post(reverse("mfa_deactivate_totp"))
        self.assertTrue(Authenticator.objects.filter(user=sophie, type=Authenticator.Type.TOTP).exists())

    def test_possible_sinon(self):
        client = Utilisateur.objects.create_user("client@exemple.fr", MOT_DE_PASSE)
        donne_role(client, "client")
        connecte_avec_double_auth(self.client, client)
        self.client.post(reverse("mfa_deactivate_totp"))
        self.assertFalse(Authenticator.objects.filter(user=client, type=Authenticator.Type.TOTP).exists())
        self.assertTrue(EvenementAcces.objects.filter(action="double_auth", objet="retrait:totp").exists())

    def test_export_rgpd_sans_secret(self):
        client = Utilisateur.objects.create_user("client@exemple.fr", MOT_DE_PASSE)
        totp = connecte_avec_double_auth(self.client, client)
        contenu = self.client.get(reverse("comptes:export_donnees")).content.decode()
        self.assertIn('"double_authentification_active": true', contenu)
        self.assertIn('"totp"', contenu)
        self.assertNotIn(totp.data["secret"], contenu)
        self.assertNotIn(AdaptateurDoubleAuth().decrypt(totp.data["secret"]), contenu)
