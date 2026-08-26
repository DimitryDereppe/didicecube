# Relations et cardinalités du projet

Pour chaque lien entre des entités, combien de représentations peut-il y
avoir de la première entité vers la seconde ? Et inversement ?

## UTILISATEUR — PROGRESSION (posséder)

- Un UTILISATEUR possède **zéro à plusieurs** PROGRESSION — cardinalité **0,n**
- Une PROGRESSION appartient à **exactement un** UTILISATEUR — cardinalité **1,1**

## UTILISATEUR — SKIN (télécharger)

- Un UTILISATEUR télécharge **zéro à plusieurs** SKIN — cardinalité **0,n**
- Un SKIN appartient à **exactement un** UTILISATEUR — cardinalité **1,1**

## SKIN — IMAGE_SKIN (composer)

- Un SKIN se compose de **zéro à plusieurs** IMAGE_SKIN — cardinalité **0,n**
- Une IMAGE_SKIN appartient à **exactement un** SKIN — cardinalité **1,1**

> ⚠️ Règle de gestion (non modélisable par une cardinalité Merise standard,
> qui ne connaît que 0,1 / 1,1 / 0,n / 1,n) : un même skin ne peut pas avoir
> **deux images pour la même couleur**. Contrairement aux règles habituelles
> de ce type (vérifiées en Service, cf. exemples SB09), celle-ci porte sur
> deux colonnes d'une même table et se modélise très bien par une contrainte
> `UNIQUE (skin_id, couleur)` — portée directement au MPD (modèle
> Sequelize), pas dans le Service.
