# Didicecube

Site de résolution de Rubik's Cube : indiquez l'état de départ de votre cube
(à la main, ou par photo) depuis une interface visuelle en 3D, personnalisable
avec des skins, et obtenez la solution — expliquée à l'écrit, rejouée
visuellement étape par étape, ou en lecture continue.

> 🚧 Projet en cours de démarrage — ce README sera complété au fil de
> l'avancement.

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
  progression, pour reprendre une résolution plus tard.

## Stack

Stack enseignée par O'Clock, en deux parties :

- **`api/`** — Node.js/Express (API REST), PostgreSQL (requêtes paramétrées,
  pattern DataMapper), Argon2 (mots de passe), JWT (sessions), Joi
  (validation), `multer` (upload de skins/photos).
- **`client/`** — Svelte + Vite. Cube rendu en CSS 3D (pas de librairie 3D
  externe). Algorithme de résolution codé à la main (méthode couche par
  couche).

## Prérequis

- [Node.js](https://nodejs.org/) (version LTS recommandée)
- npm (fourni avec Node.js)
- [PostgreSQL](https://www.postgresql.org/) (pour les comptes/progression)

## Installation

```bash
git clone <url-du-dépôt>
cd didicecube

# API
cd api
npm install
cp .env.example .env   # une fois le fichier .env.example ajouté au projet

# Client (dans un autre terminal)
cd ../client
npm install
```

## Variables d'environnement

À définir dans `api/.env` une fois `api/.env.example` ajouté au projet : port
du serveur, connexion PostgreSQL, secret JWT, dossier de stockage des
fichiers téléchargés (skins/photos).

## Scripts disponibles

### `api/`

- `npm run dev` — démarre le serveur avec rechargement automatique (nodemon).
- `npm start` — démarre le serveur.
- `npm test` — lance les tests.

### `client/`

- `npm run dev` — démarre le serveur de développement Vite.
- `npm run build` — build de production.

## Structure des dossiers

```
didicecube/
├── api/           # Backend Express (API REST)
│   └── package.json
├── client/        # Frontend Svelte + Vite
│   └── package.json
└── README.md
```

*(à compléter au fur et à mesure de la mise en place de l'architecture)*

## Déploiement

Le site est destiné à être déployé sur le serveur **Aldebaran** et accessible
depuis le réseau local.

## Licence

ISC
