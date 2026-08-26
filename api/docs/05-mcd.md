# Modèle conceptuel de données

Schéma complet : voir [05-MCD.svg](05-MCD.svg) — construit à la main dans le
style visuel de Mocodo (le paquet `mocodo` n'est pas installable dans cet
environnement de développement : ni `pip`, ni accès réseau vers PyPI). En
alternative directement lisible sur GitHub/VS Code, un diagramme Mermaid
équivalent est fourni plus bas.

Source Mocodo (texte) : [mocodo-source.mcd](mocodo-source.mcd)

## Entités

- UTILISATEUR
- PROGRESSION
- SKIN
- IMAGE_SKIN

## Relations et cardinalités

- POSSEDER : UTILISATEUR (0,n) — (1,1) PROGRESSION
- TELECHARGER : UTILISATEUR (0,n) — (1,1) SKIN
- COMPOSER : SKIN (0,n) — (1,1) IMAGE_SKIN

## Diagramme Mermaid (équivalent, rendu natif GitHub/VS Code)

```mermaid
erDiagram
    UTILISATEUR ||--o{ PROGRESSION : possede
    UTILISATEUR ||--o{ SKIN : telecharge
    SKIN ||--o{ IMAGE_SKIN : compose

    UTILISATEUR {
        int id_utilisateur PK
        string email
        string pseudo
        string mot_de_passe_hash
        datetime date_inscription
    }
    PROGRESSION {
        int id_progression PK
        string etat_depart
        int etape_courante
        datetime date_creation
        datetime date_maj
        int id_utilisateur FK
    }
    SKIN {
        int id_skin PK
        string nom_skin
        datetime date_ajout
        int id_utilisateur FK
    }
    IMAGE_SKIN {
        int id_image_skin PK
        string couleur
        string chemin_fichier
        int id_skin FK
    }
```
