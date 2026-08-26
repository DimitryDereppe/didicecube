# Tests — Didicecube API

Deux familles de tests, complémentaires :

## `http/*.http` — tests manuels des routes

Un fichier par ressource (`utilisateurs.http`, `sessions.http`,
`progressions.http`), au format [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)
(extension VS Code). Chaque requête est commentée avec le code HTTP attendu.

**Prérequis** :

```bash
npm run migrate   # crée/synchronise les tables
npm run seed      # données de démo (compte : demo@example.com / Cube1234!)
npm run dev       # démarre l'API (par défaut sur le port de .env, PORT)
```

Puis ouvrir un fichier `.http` dans VS Code et cliquer sur « Send Request »
au-dessus de chaque requête. Le cookie de session posé par une connexion est
automatiquement réutilisé par les requêtes suivantes du fichier (cookie jar
de l'extension) — pas besoin de le recopier à la main.

⚠️ Si le port par défaut (3000) est déjà pris par un autre projet en local,
adapter la variable `@baseUrl` en tête de chaque fichier.

## `*.test.js` — tests unitaires (`node:test`)

Logique **pure**, sans BDD ni serveur : schémas de validation Joi
(`validation.test.js`) et fonctions cryptographiques
(`auth.service.test.js`, hachage Argon2 + JWT). Lancés avec :

```bash
npm test
```

Ne couvrent pas les routes/controllers eux-mêmes (ça, c'est le rôle des
fichiers `.http` ci-dessus) : les tester nécessiterait une BDD de test
dédiée et une librairie d'intégration HTTP (ex. `supertest`), hors stack
enseignée pour l'instant — à introduire si le besoin devient réel.

## Règle du projet : tenir ce dossier à jour

Toute route/controller ajouté ou modifié dans `api/` s'accompagne, **dans la
même tâche**, de la mise à jour des fichiers `.http` correspondants (et des
tests unitaires si de la logique pure est ajoutée) — cf. `CLAUDE.md`.
