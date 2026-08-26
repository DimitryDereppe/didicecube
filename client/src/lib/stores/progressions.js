// Store partagé : progressions sauvegardées de l'utilisateur connecté.
// Centralise les appels à /progressions — SaisieCube et MesProgressions
// restent synchronisés automatiquement sans se connaître (cf. DRY).
import { writable } from "svelte/store";
import { api } from "../api.js";

/** @type {import("svelte/store").Writable<Array<object>>} */
export const progressions = writable([]);

/** Recharge la liste depuis l'API. */
export async function chargerProgressions() {
  progressions.set(await api.get("/progressions"));
}

/**
 * Sauvegarde un nouvel état de cube, puis recharge la liste.
 * @param {string} etatDepart - Chaîne de 54 caractères (cf. cube.js).
 */
export async function creerProgression(etatDepart) {
  await api.post("/progressions", { etat_depart: etatDepart });
  await chargerProgressions();
}

/** Supprime une progression, puis recharge la liste. */
export async function supprimerProgression(id) {
  await api.delete(`/progressions/${id}`);
  await chargerProgressions();
}
