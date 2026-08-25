# Didicecube

Site de résolution de Rubik's Cube : indiquez l'état de départ de votre cube
depuis une interface visuelle, et obtenez la solution — expliquée à l'écrit,
rejouée visuellement étape par étape, ou en lecture continue.

> 🚧 Projet en cours de démarrage — ce README sera complété au fil de
> l'avancement (voir [CARNET-DE-BORD-RUBICUBE.md](CARNET-DE-BORD-RUBICUBE.md)
> pour le suivi détaillé).

## Fonctionnalités

- **Saisie du cube** : une interface visuelle pour renseigner la couleur de
  chaque face/sticker de l'état de départ.
- **Résolution à l'écrit** : la liste des mouvements (notation du cube) avec
  une explication de chaque étape.
- **Résolution visuelle pas à pas** : le cube affiché avance d'un mouvement à
  la fois, à la demande.
- **Résolution en continu** : lecture automatique et animée de la résolution
  complète.

## Stack

Stack enseignée par O'Clock : Node.js/Express côté serveur, HTML/CSS/JS pour
l'interface. Le détail précis de l'architecture (rendu du cube, algorithme de
résolution, besoin ou non d'une base de données) reste à trancher — voir le
carnet de bord.

## Prérequis

- [Node.js](https://nodejs.org/) (version LTS recommandée)
- npm (fourni avec Node.js)

## Installation

```bash
git clone <url-du-dépôt>
cd didicecube
npm install
cp .env.example .env   # une fois le fichier .env.example ajouté au projet
```

## Variables d'environnement

Aucune pour l'instant. Un `.env.example` sera ajouté dès que le projet en
aura besoin (port du serveur, éventuelle connexion base de données...).

## Scripts disponibles

Aucun script applicatif pour l'instant (`npm test` est le script par défaut
généré par `npm init`, à remplacer dès que des tests seront écrits).

## Structure des dossiers

```
didicecube/
├── CLAUDE.md                    # Standards de développement du projet
├── CARNET-DE-BORD-RUBICUBE.md   # Journal de bord du projet
├── package.json
└── .gitignore
```

*(à compléter au fur et à mesure de la mise en place de l'architecture)*

## Déploiement

Le site est destiné à être déployé sur le serveur **Aldebaran** et accessible
depuis le réseau local.

## Licence

ISC
