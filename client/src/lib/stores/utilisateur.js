// Store partagé : utilisateur actuellement connecté (ou non). Un seul point
// de vérité pour toute l'app, plutôt que chaque composant refasse son appel
// API — cf. DRY.
import { writable } from "svelte/store";
import { api } from "../api.js";

// undefined = session pas encore vérifiée (chargement initial),
// null = pas connecté, objet = connecté (id, email, pseudo, date_inscription).
export const utilisateurConnecte = writable(undefined);

/** Vérifie la session actuelle auprès de l'API — à appeler au chargement de l'app. */
export async function verifierSession() {
  try {
    const utilisateur = await api.get("/utilisateurs/moi");
    utilisateurConnecte.set(utilisateur);
  } catch {
    // Pas de cookie, ou cookie expiré/invalide : simplement "non connecté",
    // pas une erreur à afficher à l'utilisateur.
    utilisateurConnecte.set(null);
  }
}

/**
 * Inscription — connecte automatiquement (l'API pose le cookie de session
 * dès l'inscription, cf. api/controllers/utilisateurs.controller.js).
 * @throws {Error} Message à afficher tel quel (ex. "Un compte existe déjà...").
 */
export async function inscrire(donnees) {
  const utilisateur = await api.post("/utilisateurs", donnees);
  utilisateurConnecte.set(utilisateur);
}

/** @throws {Error} Message à afficher tel quel (ex. "Email ou mot de passe incorrect."). */
export async function connecter(identifiants) {
  const utilisateur = await api.post("/sessions", identifiants);
  utilisateurConnecte.set(utilisateur);
}

export async function deconnecter() {
  await api.delete("/sessions");
  utilisateurConnecte.set(null);
}
