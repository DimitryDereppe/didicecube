// Controller : orchestration des requêtes/réponses pour les skins et leurs
// images. Comme pour les progressions, chaque accès à un skin précis
// vérifie qu'il appartient bien à l'utilisateur connecté (authentification
// ≠ autorisation) — 404 si absent ou appartenant à quelqu'un d'autre.
import fs from "node:fs/promises";
import path from "node:path";
import { Skin, ImageSkin } from "../models/index.js";
import { EXTENSIONS_PAR_TYPE } from "../config/upload.js";

const DOSSIER_UPLOADS = process.env.UPLOAD_DIR || "uploads";

/** Chemin absolu d'un fichier dont le chemin relatif est stocké en base. */
function versCheminAbsolu(cheminRelatif) {
  return path.join(DOSSIER_UPLOADS, cheminRelatif);
}

/** Supprime un fichier du disque sans faire échouer l'appelant s'il est déjà absent. */
async function supprimerFichierSiPresent(cheminRelatif) {
  await fs.unlink(versCheminAbsolu(cheminRelatif)).catch(() => {});
}

async function trouverSkinDeLUtilisateur(id, idUtilisateur) {
  const skin = await Skin.findByPk(id, { include: "images" });
  if (!skin || skin.utilisateur_id !== idUtilisateur) {
    return null;
  }
  return skin;
}

/** POST /skins — crée un skin (sans image pour l'instant). */
export async function creer(req, res, next) {
  try {
    const skin = await Skin.create({
      nom_skin: req.body.nom_skin,
      utilisateur_id: req.utilisateur.id,
    });
    res.status(201).json(skin);
  } catch (error) {
    console.error("Erreur lors de la création d'un skin", {
      utilisateur: req.utilisateur.id,
      error: error.message,
    });
    next(error);
  }
}

/** GET /skins — liste les skins de l'utilisateur connecté, avec leurs images. */
export async function lister(req, res, next) {
  try {
    const skins = await Skin.findAll({
      where: { utilisateur_id: req.utilisateur.id },
      include: "images",
      order: [["date_ajout", "DESC"]],
    });
    res.json(skins);
  } catch (error) {
    console.error("Erreur lors de la liste des skins", {
      utilisateur: req.utilisateur.id,
      error: error.message,
    });
    next(error);
  }
}

/** GET /skins/:id — récupère un skin précis avec ses images. */
export async function recuperer(req, res, next) {
  try {
    const skin = await trouverSkinDeLUtilisateur(req.params.id, req.utilisateur.id);
    if (!skin) {
      return res.status(404).json({ message: "Skin introuvable." });
    }
    res.json(skin);
  } catch (error) {
    console.error("Erreur lors de la récupération d'un skin", {
      id: req.params.id,
      error: error.message,
    });
    next(error);
  }
}

/** DELETE /skins/:id — supprime un skin et ses images (fichiers + BDD). */
export async function supprimer(req, res, next) {
  try {
    const skin = await trouverSkinDeLUtilisateur(req.params.id, req.utilisateur.id);
    if (!skin) {
      return res.status(404).json({ message: "Skin introuvable." });
    }
    // La suppression BDD cascade sur image_skin (ON DELETE CASCADE), mais
    // les fichiers sur disque ne sont pas gérés par PostgreSQL : à nettoyer
    // nous-mêmes, avant que les lignes ne disparaissent.
    await Promise.all(skin.images.map((image) => supprimerFichierSiPresent(image.chemin_fichier)));
    await skin.destroy();
    res.status(204).end();
  } catch (error) {
    console.error("Erreur lors de la suppression d'un skin", {
      id: req.params.id,
      error: error.message,
    });
    next(error);
  }
}

/**
 * POST /skins/:id/images — ajoute ou remplace l'image d'une couleur pour ce
 * skin (upsert : une seconde upload pour la même couleur remplace la
 * précédente plutôt que d'échouer, cf. contrainte UNIQUE(skin_id, couleur)).
 */
export async function ajouterImage(req, res, next) {
  try {
    const skin = await trouverSkinDeLUtilisateur(req.params.id, req.utilisateur.id);
    if (!skin) {
      return res.status(404).json({ message: "Skin introuvable." });
    }
    if (!req.file) {
      return res.status(400).json({ message: "Fichier image requis (champ \"image\")." });
    }

    const { couleur } = req.body;
    const extension = EXTENSIONS_PAR_TYPE[req.file.mimetype];
    const cheminRelatif = path.join("skins", String(skin.id), `${couleur}${extension}`);

    let image = await ImageSkin.findOne({ where: { skin_id: skin.id, couleur } });
    if (image) {
      // Remplacement : si l'ancienne image avait une autre extension
      // (png -> webp par ex.), l'ancien fichier ne serait jamais écrasé
      // par le nouveau chemin — on le supprime explicitement.
      if (image.chemin_fichier !== cheminRelatif) {
        await supprimerFichierSiPresent(image.chemin_fichier);
      }
    }

    await fs.mkdir(path.dirname(versCheminAbsolu(cheminRelatif)), { recursive: true });
    await fs.writeFile(versCheminAbsolu(cheminRelatif), req.file.buffer);

    if (image) {
      image.chemin_fichier = cheminRelatif;
      await image.save();
    } else {
      image = await ImageSkin.create({ skin_id: skin.id, couleur, chemin_fichier: cheminRelatif });
    }

    res.status(201).json(image);
  } catch (error) {
    console.error("Erreur lors de l'ajout d'une image de skin", {
      skin: req.params.id,
      error: error.message,
    });
    next(error);
  }
}

/** DELETE /skins/:id/images/:couleur — retire l'image d'une couleur. */
export async function supprimerImage(req, res, next) {
  try {
    const skin = await trouverSkinDeLUtilisateur(req.params.id, req.utilisateur.id);
    if (!skin) {
      return res.status(404).json({ message: "Skin introuvable." });
    }
    const image = await ImageSkin.findOne({
      where: { skin_id: skin.id, couleur: req.params.couleur },
    });
    if (!image) {
      return res.status(404).json({ message: "Aucune image pour cette couleur." });
    }
    await supprimerFichierSiPresent(image.chemin_fichier);
    await image.destroy();
    res.status(204).end();
  } catch (error) {
    console.error("Erreur lors de la suppression d'une image de skin", {
      skin: req.params.id,
      couleur: req.params.couleur,
      error: error.message,
    });
    next(error);
  }
}
