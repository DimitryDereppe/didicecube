# Entités et propriétés du projet

- De quelles données est composée chaque entité ?
- Quelles propriétés permettent d'identifier de façon unique chaque entité ?

## UTILISATEUR

- id_utilisateur : identifiant unique de l'utilisateur
- email : adresse email, sert d'identifiant de connexion
- pseudo : pseudo affiché
- mot_de_passe_hash : mot de passe de l'utilisateur — jamais stocké en
  clair, seul son **hash** (Argon2) est conservé
- date_inscription : date de création du compte

## PROGRESSION

- id_progression : identifiant unique de la progression sauvegardée
- etat_depart : état de départ du cube (couleur des 54 stickers)
- etape_courante : index du mouvement où l'utilisateur s'est arrêté dans la
  résolution
- date_creation : date de création de la progression
- date_maj : date de la dernière sauvegarde

## SKIN

- id_skin : identifiant unique du skin
- nom_skin : nom donné au skin par son auteur
- date_ajout : date d'ajout du skin

## IMAGE_SKIN

- id_image_skin : identifiant unique de l'image
- couleur : couleur standard du cube que cette image remplace (blanc,
  jaune, rouge, orange, vert ou bleu)
- chemin_fichier : chemin/nom du fichier image stocké sur le serveur
