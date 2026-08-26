// Controller : orchestration des requêtes/réponses pour les progressions
// sauvegardées. Toutes les routes sont protégées (cf. progressions.routes.js) :
// req.utilisateur est garanti présent. Chaque accès à une progression précise
// vérifie en plus qu'elle appartient bien à l'utilisateur connecté
// (authentification ≠ autorisation).
import { Progression } from "../models/index.js";

/**
 * Récupère une progression par id en vérifiant qu'elle appartient à
 * l'utilisateur connecté. Renvoie null si absente ou si elle appartient à
 * quelqu'un d'autre — les deux cas sont traités en 404 par les
 * controllers appelants, pour ne pas révéler l'existence d'une progression
 * appartenant à un autre compte (cf. principe déjà appliqué à la connexion).
 */
async function trouverProgressionDeLUtilisateur(id, idUtilisateur) {
  const progression = await Progression.findByPk(id);
  if (!progression || progression.utilisateur_id !== idUtilisateur) {
    return null;
  }
  return progression;
}

/** POST /progressions — sauvegarde une nouvelle progression. */
export async function creer(req, res, next) {
  try {
    const { etat_depart, etape_courante } = req.body;
    const progression = await Progression.create({
      etat_depart,
      etape_courante,
      utilisateur_id: req.utilisateur.id,
    });
    res.status(201).json(progression);
  } catch (error) {
    console.error("Erreur lors de la création d'une progression", {
      utilisateur: req.utilisateur.id,
      error: error.message,
    });
    next(error);
  }
}

/** GET /progressions — liste les progressions de l'utilisateur connecté. */
export async function lister(req, res, next) {
  try {
    const progressions = await Progression.findAll({
      where: { utilisateur_id: req.utilisateur.id },
      order: [["date_maj", "DESC"]],
    });
    res.json(progressions);
  } catch (error) {
    console.error("Erreur lors de la liste des progressions", {
      utilisateur: req.utilisateur.id,
      error: error.message,
    });
    next(error);
  }
}

/** GET /progressions/:id — récupère une progression précise. */
export async function recuperer(req, res, next) {
  try {
    const progression = await trouverProgressionDeLUtilisateur(req.params.id, req.utilisateur.id);
    if (!progression) {
      return res.status(404).json({ message: "Progression introuvable." });
    }
    res.json(progression);
  } catch (error) {
    console.error("Erreur lors de la récupération d'une progression", {
      id: req.params.id,
      error: error.message,
    });
    next(error);
  }
}

/** PATCH /progressions/:id — met à jour l'étape atteinte (reprise de résolution). */
export async function mettreAJour(req, res, next) {
  try {
    const progression = await trouverProgressionDeLUtilisateur(req.params.id, req.utilisateur.id);
    if (!progression) {
      return res.status(404).json({ message: "Progression introuvable." });
    }
    progression.etape_courante = req.body.etape_courante;
    progression.date_maj = new Date();
    await progression.save();
    res.json(progression);
  } catch (error) {
    console.error("Erreur lors de la mise à jour d'une progression", {
      id: req.params.id,
      error: error.message,
    });
    next(error);
  }
}

/** DELETE /progressions/:id — supprime une progression sauvegardée. */
export async function supprimer(req, res, next) {
  try {
    const progression = await trouverProgressionDeLUtilisateur(req.params.id, req.utilisateur.id);
    if (!progression) {
      return res.status(404).json({ message: "Progression introuvable." });
    }
    await progression.destroy();
    res.status(204).end();
  } catch (error) {
    console.error("Erreur lors de la suppression d'une progression", {
      id: req.params.id,
      error: error.message,
    });
    next(error);
  }
}
