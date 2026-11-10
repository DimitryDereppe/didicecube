# Didicecube

Site de résolution de Rubik's Cube : indiquez l'état de départ de votre cube
(à la main, ou par photo) depuis une interface visuelle en 3D, personnalisable
avec des skins, et obtenez la solution — expliquée à l'écrit, rejouée
visuellement étape par étape, ou en lecture continue.

## Fonctionnalités

- **Saisie du cube en 3D** : une interface visuelle (cube rendu en CSS 3D)
  pour renseigner la couleur de chaque face/sticker de l'état de départ.
- **Détection par photo** : une photo par face (capture guidée dans une
  grille 3×3 affichée à l'écran) suffit à détecter automatiquement les
  couleurs, pour un cube aux couleurs standards.
- **Skins personnalisés** : possibilité de télécharger des habillages
  visuels pour le cube affiché.
- **Résolution à l'écrit** : la liste des mouvements (notation du cube) avec
  une explication de chaque étape.
- **Résolution visuelle pas à pas** : le cube affiché avance d'un mouvement à
  la fois, à la demande.
- **Résolution en continu** : lecture automatique et animée de la résolution
  complète.
- **Compte utilisateur** : enregistre l'état de départ du cube et la
  progression, pour reprendre une résolution plus tard ; export et
  suppression de ses données (RGPD).

## Pile technique

Bâti sur le **gabarit Django du socle commun** (`socle-commun/gabarit-django`) :
Django 5.2, PostgreSQL 17, django-allauth (connexion par email, double
authentification), journal d'accès, droits RGPD, onglet Accessibilité, Docker.

- **`cube/moteur.py`** : les 18 mouvements, calculés à partir de la position 3D
  de chaque sticker. Le navigateur reçoit ces mêmes permutations.
- **`cube/resolution.py`** : résolution couche par couche (méthode débutant),
  écrite à la main, avec une explication par pièce placée. Détecte les états
  impossibles (pièce retournée, coin tourné, deux pièces échangées).
- **`cube/`** : progressions, skins (images privées, servies au seul
  propriétaire), pages et appels JSON.
- **`static/js/cube.js`** : patron, cube 3D en CSS (sans bibliothèque), photo
  (couleurs détectées dans le navigateur, photos jamais envoyées), lecture pas
  à pas ou continue.

La première version (API Express + client Svelte) reste dans l'historique git.

## Démarrer

```bash
cp .env.example .env   # remplir SECRET_KEY, MFA_CLES_CHIFFREMENT, DB_PASSWORD
docker compose up --build
docker compose exec web python manage.py createsuperuser
```

Le site est sur http://localhost:8000 (port réglable : `WEB_PORT_HOTE`).
En développement, les emails (confirmation d'adresse) s'affichent dans
`docker compose logs web`.

## Vérifier

```bash
outils/verifie.sh          # ruff, tests, check --deploy, pip-audit
outils/verifie.sh rapide   # ruff + tests
```

## Mise en production

Voir le README du gabarit Django (Caddy + gunicorn, sauvegardes). Les images
des skins sont dans le volume `medias` : à inclure dans les sauvegardes.

## Documents

Conception Merise dans [docs/conception/](docs/conception/).
