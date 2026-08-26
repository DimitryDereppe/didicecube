// Options du cookie contenant le JWT de session. Centralisées ici pour que
// la pose (res.cookie) et la suppression (res.clearCookie) utilisent
// exactement les mêmes attributs — Express exige que clearCookie soit
// appelé avec les mêmes options que la création, sinon le cookie n'est pas
// supprimé côté navigateur.

// Durée de vie du cookie ET du JWT (cf. api/services/auth.service.js) :
// gardées synchronisées pour qu'un cookie encore présent corresponde
// toujours à un token qui n'a pas encore expiré côté serveur.
export const DUREE_SESSION_MS = 2 * 60 * 60 * 1000; // 2h

export const OPTIONS_COOKIE_TOKEN = {
  httpOnly: true, // inaccessible en JS côté navigateur : protection XSS (section 11)
  secure: process.env.NODE_ENV === "production", // HTTPS obligatoire seulement en prod (dev/LAN souvent en http)
  sameSite: "strict", // protection CSRF de base (section 8ter) : cookie jamais envoyé cross-site
  maxAge: DUREE_SESSION_MS,
};
