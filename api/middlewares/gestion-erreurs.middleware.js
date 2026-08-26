// Middlewares de gestion d'erreurs (cf. section 13) : l'API ne doit jamais
// renvoyer une stack trace ou un message SQL au client, ni planter sur une
// route inconnue ou une erreur inattendue.

/** Middleware 404 — dernière route, atteinte si rien d'autre n'a matché. */
export function routeIntrouvable(req, res) {
  res.status(404).json({ message: "Ressource introuvable." });
}

/** Middleware d'erreur 500 — tout dernier, capte les erreurs passées via next(err). */
export function gererErreur(err, req, res, next) {
  console.error("Erreur serveur", { url: req.originalUrl, error: err.message });
  res.status(500).json({ message: "Une erreur est survenue, réessayez plus tard." });
}
