// Controller : connexion/déconnexion — la « session » est représentée par
// le cookie JWT (cf. api/config/cookie-options.js), il n'y a pas de table
// SESSION en base.
import { Utilisateur } from "../models/index.js";
import { verifierMotDePasse, genererToken } from "../services/auth.service.js";
import { OPTIONS_COOKIE_TOKEN } from "../config/cookie-options.js";

/** POST /sessions — connexion. */
export async function connecter(req, res, next) {
  try {
    const { email, mot_de_passe } = req.body;
    const utilisateur = await Utilisateur.findOne({ where: { email } });

    // Message volontairement identique, que l'email existe ou non, et que
    // ce soit l'email ou le mot de passe qui soit faux : ne pas permettre à
    // un visiteur de deviner quels emails sont enregistrés (énumération de
    // comptes).
    const motDePasseValide =
      utilisateur && (await verifierMotDePasse(utilisateur.mot_de_passe_hash, mot_de_passe));
    if (!motDePasseValide) {
      return res.status(401).json({ message: "Email ou mot de passe incorrect." });
    }

    const token = genererToken(utilisateur);
    res.cookie("token", token, OPTIONS_COOKIE_TOKEN);
    res.json({
      id: utilisateur.id,
      email: utilisateur.email,
      pseudo: utilisateur.pseudo,
    });
  } catch (error) {
    console.error("Erreur lors de la connexion", { email: req.body?.email, error: error.message });
    next(error);
  }
}

/** DELETE /sessions — déconnexion : supprime le cookie de session. */
export function deconnecter(req, res) {
  res.clearCookie("token", OPTIONS_COOKIE_TOKEN);
  res.status(204).end();
}
