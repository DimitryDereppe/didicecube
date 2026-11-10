# Entités du projet

Quels sont les groupes de données qui interviennent dans le projet ?

## Réflexion

Périmètre couvert par la BDD (voir `CLAUDE.md`, section « Architecture
retenue ») : **comptes utilisateurs**, **progression de résolution
sauvegardée**, **skins téléchargés**. L'état du cube en cours de résolution
d'un visiteur non connecté reste transitoire (objet JS en mémoire, 6 faces ×
9 stickers) et n'entre pas dans ce modèle — on ne modélise que ce qui est
réellement persisté.

Quatre groupes de données ressortent des fonctionnalités du site :

- un **utilisateur** qui peut créer un compte, se connecter ;
- une **progression** : l'état de départ d'un cube que l'utilisateur a
  sauvegardé, et l'endroit où il s'est arrêté dans la résolution ;
- un **skin** : un habillage visuel du cube, téléchargé par un utilisateur ;
- une **image de skin** : l'image associée à un skin pour une des 6
  couleurs standards du cube (un skin peut remplacer le blanc, le jaune,
  etc. par une image différente).

## Liste des entités

- UTILISATEUR
- PROGRESSION
- SKIN
- IMAGE_SKIN
