# Modèle logique de données

Le MLD traduit le [MCD](05-mcd.md) en tables, colonnes et clés. C'est un
exercice de traduction (cf. règles de passage, section 4 de
`PROMPT-HEADER-CLAUDE.md`) :

- les entités deviennent des tables ;
- le discriminant (`id_x`) se traduit par un `id` — convention Sequelize
  (clé primaire auto-incrémentée nommée `id` par défaut sur chaque modèle) ;
- une association `One-to-Many` devient une clé étrangère nommée
  `<table>_id`, côté table qui porte la cardinalité `1,1` — convention
  Sequelize par défaut pour les associations `belongsTo`/`hasMany` ;
- pas de table de liaison ici : contrairement à SB09 (associations
  many-to-many `COMPOSER`/`POSSÉDER`), les trois associations du projet sont
  toutes `1,1` — `0,n`, donc de simples clés étrangères.

## Notation

```
utilisateur ( __id__, email, pseudo, mot_de_passe_hash, date_inscription )

progression ( __id__, etat_depart, etape_courante, date_creation,
              date_maj, utilisateur_id #FK(utilisateur.id) )

skin ( __id__, nom_skin, date_ajout, utilisateur_id #FK(utilisateur.id) )

image_skin ( __id__, couleur, chemin_fichier, skin_id #FK(skin.id) )
```

## Notes de traduction

- Noms de colonnes gardés **en français** (`mot_de_passe_hash`, `etat_depart`,
  `chemin_fichier`...) : contrairement à SB09, aucun script SQL indicatif
  externe n'impose l'anglais ici — rester cohérent avec le reste du projet
  (commentaires, noms de variables), déjà entièrement en français.
- `progression.utilisateur_id` et `skin.utilisateur_id` : traduction directe
  des associations `One-to-Many` `POSSEDER` et `TELECHARGER`. La clé
  étrangère va du côté où la cardinalité vaut `1,1` (PROGRESSION, SKIN), et
  pointe vers la clé primaire de l'entité côté `0,n` (UTILISATEUR) — cf.
  règle de traduction 1-N, section 4 de `PROMPT-HEADER-CLAUDE.md`.
- `image_skin.skin_id` : même raisonnement pour `COMPOSER` (IMAGE_SKIN est
  côté `1,1`, SKIN côté `0,n`).
- Pour que la règle « un skin ne peut pas avoir deux images de la même
  couleur » soit garantie au niveau base de données (pas seulement par
  discipline applicative), une contrainte `UNIQUE (skin_id, couleur)` est
  prévue sur `image_skin` — portée directement dans le modèle Sequelize
  (`indexes: [{ unique: true, fields: ['skin_id', 'couleur'] }]`).
- L'attribut conceptuel « mot de passe » se traduit en `mot_de_passe_hash`,
  pas `mot_de_passe` : on ne stocke jamais le mot de passe en clair (cf.
  section 10 de la charte, hachage Argon2). Cette traduction est déjà
  présente au niveau du **MLD**, avant même d'écrire le Model Sequelize — le
  nom de colonne rappelle par lui-même la contrainte de sécurité, plutôt que
  de compter sur la discipline de chacun.

## MPD

Contrairement à SB09 (qui fournit un `create_tables.sql` à titre indicatif
mais construit réellement la BDD depuis les modèles Sequelize), ce projet
n'a pas de script SQL indicatif à traduire : le MPD se matérialise
directement dans les **modèles Sequelize** (`api/models/`), qui sont la
seule source de vérité du schéma physique — voir
[api/migrations/01.create-tables.js](../migrations/01.create-tables.js).
