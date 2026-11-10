import json
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from comptes.rgpd import exporte_donnees

from . import moteur, resolution
from .models import ImageSkin, Progression, Skin

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


def echange(etat, a, b):
    e = list(etat)
    e[a], e[b] = e[b], e[a]
    return "".join(e)


class MoteurTests(SimpleTestCase):
    def test_quatre_quarts_de_tour_reviennent_au_depart(self):
        etat, _ = moteur.melange(graine=1)
        for face in moteur.FACES:
            self.assertEqual(moteur.applique(etat, [face] * 4), etat)
            self.assertEqual(moteur.applique(etat, [face, face + "'"]), etat)
            self.assertEqual(moteur.applique(etat, [face + "2"] * 2), etat)

    def test_inverse_d_une_suite(self):
        etat, mouvements = moteur.melange(graine=2)
        self.assertEqual(moteur.applique(etat, moteur.inverse(mouvements)), moteur.RESOLU)

    def test_geometrie_verifiee_a_la_main(self):
        """Quelques trajets de stickers vérifiés sur un vrai cube (case k de la face X notée X0..X8).

        L'ancien moteur JavaScript (client/src/lib/moves.js) se trompait ici : pour F, il envoyait le haut de la
        colonne de gauche (L2) sur U6 au lieu de U8.
        """
        def case(face, i):
            return moteur.FACES.index(face) * 9 + i

        trajets = {
            "F": [("U", 6, "R", 0), ("U", 8, "R", 6), ("L", 2, "U", 8), ("L", 8, "U", 6), ("R", 0, "D", 2)],
            "U": [("F", 0, "L", 0), ("F", 2, "L", 2), ("R", 0, "F", 0), ("B", 0, "R", 0)],
            "R": [("F", 2, "U", 2), ("U", 2, "B", 6), ("D", 8, "F", 8)],
        }
        for mouvement, liste in trajets.items():
            perm = moteur.MOUVEMENTS[mouvement]
            for depart, i, arrivee, j in liste:
                self.assertEqual(perm[case(arrivee, j)], case(depart, i), f"{mouvement} : {depart}{i}")

    def test_simplification(self):
        self.assertEqual(moteur.simplifie(["U", "U"]), ["U2"])
        self.assertEqual(moteur.simplifie(["R", "U", "U'", "R'"]), [])
        self.assertEqual(moteur.simplifie(["U2", "U", "F"]), ["U'", "F"])


class ResolutionTests(SimpleTestCase):
    def test_resout_des_melanges_aleatoires(self):
        for graine in range(60):
            etat, _ = moteur.melange(30, graine=graine)
            resultat = resolution.solution(etat)
            self.assertTrue(moteur.est_resolu(moteur.applique(etat, resultat["mouvements"])), graine)
            self.assertTrue(all(e["titre"] and e["explication"] for e in resultat["etapes"]))

    def test_cube_tenu_autrement(self):
        """Les centres peuvent être n'importe où : la première couche se construit sur le dessous saisi."""
        etat, _ = moteur.melange(graine=7)
        tourne = moteur.applique(etat, "R L'")  # change seulement la position, pas la difficulté
        resultat = resolution.solution(tourne)
        self.assertTrue(moteur.est_resolu(moteur.applique(tourne, resultat["mouvements"])))

    def test_cube_deja_resolu(self):
        self.assertEqual(resolution.solution(moteur.RESOLU), {"etapes": [], "mouvements": []})

    def test_etats_impossibles(self):
        etat, _ = moteur.melange(graine=3)
        arete = moteur.ARETES[0]
        coin = moteur.COINS[0]
        autre_arete = moteur.ARETES[5]
        cas = {
            "mauvais compte": "B" * 54,
            "lettre inconnue": "X" + moteur.RESOLU[1:],
            "arête retournée": echange(etat, *arete),
            "coin tourné": "".join(
                etat[coin[(coin.index(k) + 1) % 3]] if k in coin else c for k, c in enumerate(etat)
            ),
            "deux arêtes échangées": echange(echange(etat, arete[0], autre_arete[0]), arete[1], autre_arete[1]),
            "deux stickers d'une même couleur échangés entre pièces": echange(etat, arete[0], coin[0]),
        }
        for nom, faux in cas.items():
            with self.subTest(nom), self.assertRaises(resolution.EtatImpossible):
                resolution.solution(faux)


class VuesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Utilisateur = get_user_model()
        cls.alice = Utilisateur.objects.create_user("alice@exemple.fr", "un mot de passe solide")
        cls.bob = Utilisateur.objects.create_user("bob@exemple.fr", "un mot de passe solide")

    def setUp(self):
        self.media = tempfile.mkdtemp()
        reglage = override_settings(MEDIA_ROOT=self.media)
        reglage.enable()
        self.addCleanup(reglage.disable)
        self.addCleanup(shutil.rmtree, self.media, ignore_errors=True)

    def post_json(self, nom, donnees):
        return self.client.post(reverse(nom), json.dumps(donnees), content_type="application/json")

    def test_atelier_et_solution_ouverts_a_tous(self):
        self.assertEqual(self.client.get(reverse("cube:atelier")).status_code, 200)
        etat, _ = moteur.melange(graine=4)
        reponse = self.post_json("cube:solution", {"etat": etat})
        self.assertEqual(reponse.status_code, 200)
        self.assertTrue(moteur.est_resolu(moteur.applique(etat, reponse.json()["mouvements"])))

    def test_solution_refuse_un_etat_faux(self):
        reponse = self.post_json("cube:solution", {"etat": "B" * 54})
        self.assertEqual(reponse.status_code, 400)
        self.assertIn("9 stickers", reponse.json()["erreur"])
        reponse = self.client.post(reverse("cube:solution"), "pas du json", content_type="application/json")
        self.assertEqual(reponse.status_code, 400)

    def test_enregistrer_demande_une_connexion(self):
        reponse = self.post_json("cube:enregistrer", {"etat": moteur.RESOLU, "etape": 0})
        self.assertEqual(reponse.status_code, 401)

    def test_enregistrer_puis_mettre_a_jour(self):
        self.client.force_login(self.alice)
        etat, _ = moteur.melange(graine=5)
        identifiant = self.post_json("cube:enregistrer", {"etat": etat, "etape": 3}).json()["id"]
        reponse = self.post_json("cube:enregistrer", {"etat": etat, "etape": 12, "id": identifiant})
        self.assertEqual(reponse.status_code, 200)
        progression = Progression.objects.get()
        self.assertEqual((progression.utilisateur, progression.etape_courante), (self.alice, 12))
        self.assertEqual(self.post_json("cube:enregistrer", {"etat": "B" * 54, "etape": 0}).status_code, 400)
        self.assertEqual(self.post_json("cube:enregistrer", {"etat": etat, "etape": -1}).status_code, 400)

    def test_progressions_d_autrui_inaccessibles(self):
        p = Progression.objects.create(utilisateur=self.bob, etat_depart=moteur.RESOLU)
        self.client.force_login(self.alice)
        self.assertNotContains(self.client.get(reverse("cube:progressions")), "Reprendre")
        self.assertEqual(self.client.get(reverse("cube:atelier"), {"progression": p.id}).status_code, 404)
        reponse = self.post_json("cube:enregistrer", {"etat": moteur.RESOLU, "etape": 1, "id": p.id})
        self.assertEqual(reponse.status_code, 404)
        self.client.post(reverse("cube:progression_supprimer", args=[p.id]))
        self.assertTrue(Progression.objects.filter(pk=p.id).exists())

    def test_supprimer_sa_progression(self):
        p = Progression.objects.create(utilisateur=self.alice, etat_depart=moteur.RESOLU)
        self.client.force_login(self.alice)
        self.assertContains(self.client.get(reverse("cube:atelier"), {"progression": p.id}), f'"progression": {{"id": {p.id}')
        self.client.post(reverse("cube:progression_supprimer", args=[p.id]))
        self.assertFalse(Progression.objects.exists())

    def test_ajout_de_skin_et_image_privee(self):
        self.client.force_login(self.alice)
        reponse = self.client.post(
            reverse("cube:skins"),
            {"nom_skin": "Mon chat", "image_B": SimpleUploadedFile("chat.png", PNG, "image/png")},
        )
        self.assertRedirects(reponse, reverse("cube:skins"))
        image = ImageSkin.objects.get()
        self.assertEqual((image.skin.nom_skin, image.couleur), ("Mon chat", "B"))
        self.assertNotIn("chat", image.fichier.name)  # nom d'origine non gardé
        reponse = self.client.get(reverse("cube:image_skin", args=[image.id]))
        self.assertEqual((reponse.status_code, reponse["Content-Type"]), (200, "image/png"))
        self.client.force_login(self.bob)
        self.assertEqual(self.client.get(reverse("cube:image_skin", args=[image.id])).status_code, 404)

    def test_skin_refuse_les_faux_fichiers(self):
        self.client.force_login(self.alice)
        for fichier in (
            SimpleUploadedFile("x.svg", b"<svg onload=alert(1)>", "image/svg+xml"),
            SimpleUploadedFile("x.png", b"\x89PNG\r\n\x1a\n" + b"0" * (2 * 1024 * 1024), "image/png"),
        ):
            reponse = self.client.post(reverse("cube:skins"), {"nom_skin": "Faux", "image_J": fichier})
            self.assertEqual(reponse.status_code, 200)
        self.client.post(reverse("cube:skins"), {"nom_skin": "Vide"})
        self.assertFalse(Skin.objects.exists())

    def test_suppression_du_skin_efface_le_fichier(self):
        self.client.force_login(self.alice)
        self.client.post(reverse("cube:skins"), {"nom_skin": "A", "image_V": SimpleUploadedFile("a.png", PNG)})
        image = ImageSkin.objects.get()
        stockage, nom = image.fichier.storage, image.fichier.name
        self.assertTrue(stockage.exists(nom))
        self.client.post(reverse("cube:skin_supprimer", args=[image.skin_id]))
        self.assertFalse(stockage.exists(nom))

    def test_export_rgpd_contient_progressions_et_skins(self):
        Progression.objects.create(utilisateur=self.alice, etat_depart=moteur.RESOLU, etape_courante=4)
        Skin.objects.create(utilisateur=self.alice, nom_skin="Bois")
        donnees = exporte_donnees(self.alice)
        self.assertEqual(donnees["progressions"][0]["etape_courante"], 4)
        self.assertEqual(donnees["skins"][0]["nom"], "Bois")
