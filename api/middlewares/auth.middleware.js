// Middleware transverse : protège une route en exigeant une session valide
// (JWT dans un cookie httpOnly, cf. api/config/cookie-options.js).
import { verifierToken } from "../services/auth.service.js";

/**
 * Bloque la requête avec 401 si aucun token valide n'est présent, sinon
 * attache le payload décodé à req.utilisateur et passe la main.
 */
export function protegerRoute(req, res, next) {
  const token = req.cookies?.token;

  if (!token) {
    return res.status(401).json({ message: "Authentification requise." });
  }

  try {
    req.utilisateur = verifierToken(token);
    next();
  } catch (error) {
    // Token expiré ou signature invalide : jamais la stack trace au client
    // (section 13), juste un message générique.
    console.error("Token JWT invalide ou expiré", { error: error.message });
    res.status(401).json({ message: "Session invalide, reconnectez-vous." });
  }
}
