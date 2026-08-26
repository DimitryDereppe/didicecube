// Controller : orchestration des requêtes/réponses pour les comptes
// utilisateurs. Aucune requête SQL ici (délégué au modèle Sequelize), aucun
// HTML (cf. section 3, SoC).
import { Op } from "sequelize";
import { Utilisateur } from "../models/index.js";
import { hacherMotDePasse, genererToken } from "../services/auth.service.js";
import { OPTIONS_COOKIE_TOKEN } from "../config/cookie-options.js";

// Champs jamais exposés au client : mot_de_passe_hash en particulier
// (cf. section 12). On ne fait jamais res.json(utilisateur) brut.
const CHAMPS_PUBLICS = ["id", "email", "pseudo", "date_inscription"];

/**
 * POST /utilisateurs — inscription. Crée le compte, hache le mot de passe,
 * puis connecte directement l'utilisateur (pose le cookie de session).
 */
export async function inscrire(req, res, next) {
  try {
    const { email, pseudo, mot_de_passe } = req.body;

    const dejaExistant = await Utilisateur.findOne({
      where: { [Op.or]: [{ email }, { pseudo }] },
    });
    if (dejaExistant) {
      // Message volontairement vague : ne pas révéler si c'est l'email ou
      // le pseudo qui est déjà pris (énumération de comptes) — même
      // logique que la connexion, cf. sessions.controller.js. Le détail
      // reste dans les logs serveur pour le débogage.
      console.error("Inscription refusée : email ou pseudo déjà utilisé", { email, pseudo });
      return res.status(409).json({ message: "Un compte existe déjà avec ces informations." });
    }

    const utilisateur = await Utilisateur.create({
      email,
      pseudo,
      mot_de_passe_hash: await hacherMotDePasse(mot_de_passe),
    });

    const token = genererToken(utilisateur);
    res.cookie("token", token, OPTIONS_COOKIE_TOKEN);

    res.status(201).json({
      id: utilisateur.id,
      email: utilisateur.email,
      pseudo: utilisateur.pseudo,
      date_inscription: utilisateur.date_inscription,
    });
  } catch (error) {
    console.error("Erreur lors de l'inscription", { email: req.body?.email, error: error.message });
    next(error);
  }
}

/**
 * GET /utilisateurs/moi — renvoie le compte actuellement connecté
 * (protégé par le middleware protegerRoute).
 */
export async function recupererUtilisateurConnecte(req, res, next) {
  try {
    const utilisateur = await Utilisateur.findByPk(req.utilisateur.id, {
      attributes: CHAMPS_PUBLICS,
    });
    if (!utilisateur) {
      // Cas rare : le compte a été supprimé après l'émission du token.
      return res.status(404).json({ message: "Utilisateur introuvable." });
    }
    res.json(utilisateur);
  } catch (error) {
    console.error("Erreur lors de la récupération du compte", { error: error.message });
    next(error);
  }
}
