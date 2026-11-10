# Dictionnaire de données

Pour chaque propriété du MCD : son code, sa désignation, son type, l'entité
à laquelle elle appartient et les remarques utiles (clé, contrainte,
exemple).

| Code | Désignation | Type | Entité | Remarques |
| --- | --- | --- | --- | --- |
| id_utilisateur | Identifiant de l'utilisateur | Entier | UTILISATEUR | Clé primaire |
| email | Adresse email de l'utilisateur | Texte | UTILISATEUR | Obligatoire, unique, format email |
| pseudo | Pseudo affiché | Texte | UTILISATEUR | Obligatoire, unique |
| mot_de_passe_hash | Mot de passe (haché) | Texte (hash Argon2) | UTILISATEUR | Obligatoire, jamais stocké/renvoyé en clair |
| date_inscription | Date de création du compte | Date/heure | UTILISATEUR | Obligatoire, valeur par défaut = date courante |
| id_progression | Identifiant de la progression | Entier | PROGRESSION | Clé primaire |
| etat_depart | État de départ du cube (54 stickers) | Texte (chaîne de 54 caractères) | PROGRESSION | Obligatoire, chaque caractère ∈ {B, J, R, O, V, L} |
| etape_courante | Index du mouvement où l'utilisateur s'est arrêté | Entier | PROGRESSION | Obligatoire, ≥ 0, par défaut 0 |
| date_creation | Date de création de la progression | Date/heure | PROGRESSION | Obligatoire, valeur par défaut = date courante |
| date_maj | Date de dernière sauvegarde | Date/heure | PROGRESSION | Obligatoire, mise à jour à chaque sauvegarde |
| id_skin | Identifiant du skin | Entier | SKIN | Clé primaire |
| nom_skin | Nom donné au skin | Texte | SKIN | Obligatoire |
| date_ajout | Date d'ajout du skin | Date/heure | SKIN | Obligatoire, valeur par défaut = date courante |
| id_image_skin | Identifiant de l'image de skin | Entier | IMAGE_SKIN | Clé primaire |
| couleur | Couleur standard remplacée par cette image | Texte (énumération) | IMAGE_SKIN | Obligatoire, ∈ {blanc, jaune, rouge, orange, vert, bleu} |
| chemin_fichier | Chemin/nom du fichier image stocké | Texte | IMAGE_SKIN | Obligatoire |

## Règles de gestion (hors dictionnaire, mais utiles pour la suite)

- Un skin ne peut pas avoir deux images pour la même couleur.
- La liste des mouvements de la solution n'est **pas stockée** : elle est
  dérivée d'`etat_depart` par l'algorithme à chaque affichage (donnée
  calculable, cf. section 4 de `PROMPT-HEADER-CLAUDE.md`).

La première règle se modélise directement en base par une contrainte
`UNIQUE (skin_id, couleur)` (portée au MPD/modèle Sequelize) — contrairement
à des règles comme « 6 Pokémon maximum par équipe » (cf. exemples SB09,
vérifiées en Service), celle-ci porte sur deux colonnes d'une même table et
n'a pas besoin de logique applicative.

## Version 2 (2026-11-10) : passage au gabarit Django du socle commun

L'API Express/Sequelize est remplacée par Django (gabarit `socle-commun/gabarit-django`). Le modèle
garde les mêmes entités ; ce qui change :

| Avant (v1, Sequelize) | Maintenant (v2, Django) |
| --- | --- |
| `utilisateur` (email, pseudo, mot_de_passe_hash, date_inscription) | `comptes.Utilisateur` du socle : connexion par **email** (plus de pseudo), mot de passe haché argon2 (`password`), `date_joined` |
| `progression.utilisateur_id` | `cube_progression.utilisateur_id` (suppression en cascade avec le compte) |
| `skin` sans propriétaire explicite dans la table | `cube_skin.utilisateur_id` : chaque skin appartient à un compte |
| `image_skin.chemin_fichier` | `cube_imageskin.fichier` (chemin relatif dans `media/skins/`, nom aléatoire) ; couleur codée sur une lettre (B, J, R, O, V, L) |
| `UNIQUE (skin_id, couleur)` | contrainte `une_image_par_couleur` |

Le modèle physique fait foi dans `cube/models.py` et `cube/migrations/`.
