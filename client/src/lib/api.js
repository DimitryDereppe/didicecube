// Petit client HTTP vers l'API Didicecube : centralise l'URL de base, les
// credentials (cookie de session httpOnly) et la gestion générique des
// erreurs. Aucune logique métier ici (cf. section 3, SoC).
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:3000";

/**
 * Effectue une requête JSON vers l'API et renvoie le corps de la réponse.
 * `credentials: "include"` est indispensable : sans ça, le cookie httpOnly
 * de session ne serait jamais envoyé (requête cross-origin en dev, client
 * sur le port Vite, API sur un autre port).
 * @throws {Error} Avec le message renvoyé par l'API si la réponse n'est pas ok.
 */
async function requete(chemin, options = {}) {
  const reponse = await fetch(`${BASE_URL}${chemin}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  // 204 No Content (ex. déconnexion) : pas de corps à parser.
  const corps = reponse.status === 204 ? null : await reponse.json().catch(() => null);

  if (!reponse.ok) {
    throw new Error(corps?.message || "Une erreur est survenue, réessayez plus tard.");
  }
  return corps;
}

export const api = {
  get: (chemin) => requete(chemin),
  post: (chemin, donnees) => requete(chemin, { method: "POST", body: JSON.stringify(donnees) }),
  patch: (chemin, donnees) => requete(chemin, { method: "PATCH", body: JSON.stringify(donnees) }),
  delete: (chemin) => requete(chemin, { method: "DELETE" }),
};
