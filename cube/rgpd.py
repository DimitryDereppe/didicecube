"""Données du cube ajoutées à l'export RGPD (voir comptes/rgpd.py et EXPORT_DONNEES_FONCTIONS)."""


def donnees_cube(utilisateur):
    return {
        "progressions": [
            {
                "etat_depart": p.etat_depart,
                "etape_courante": p.etape_courante,
                "creee_le": p.date_creation.isoformat(),
                "modifiee_le": p.date_maj.isoformat(),
            }
            for p in utilisateur.progressions.all()
        ],
        "skins": [
            {
                "nom": s.nom_skin,
                "ajoute_le": s.date_ajout.isoformat(),
                "images": {i.get_couleur_display(): i.fichier.name for i in s.images.all()},
            }
            for s in utilisateur.skins.prefetch_related("images")
        ],
    }
