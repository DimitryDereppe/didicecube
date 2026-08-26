// Service : opérations cryptographiques liées à l'authentification
// (hachage/vérification de mot de passe, génération/vérification de JWT).
// Aucun accès BDD ni HTTP ici — uniquement de la logique réutilisable,
// appelée par les controllers (cf. section 3, SoC).
import argon2 from "argon2";
import jwt from "jsonwebtoken";
import { DUREE_SESSION_MS } from "../config/cookie-options.js";

/**
 * Hache un mot de passe en clair avec Argon2id (cf. section 10).
 * @param {string} motDePasse - Mot de passe saisi par l'utilisateur.
 * @returns {Promise<string>} Le hash à stocker en base.
 */
export async function hacherMotDePasse(motDePasse) {
  return argon2.hash(motDePasse, { type: argon2.argon2id });
}

/**
 * Vérifie qu'un mot de passe en clair correspond à un hash stocké.
 * @param {string} hash - Hash stocké en base (mot_de_passe_hash).
 * @param {string} motDePasseSaisi - Mot de passe saisi à la connexion.
 * @returns {Promise<boolean>} true si le mot de passe correspond.
 */
export async function verifierMotDePasse(hash, motDePasseSaisi) {
  return argon2.verify(hash, motDePasseSaisi);
}

/**
 * Génère un JWT de session pour un utilisateur.
 * Payload volontairement minimal et public (jamais le hash du mot de passe
 * ni une autre donnée sensible) — cf. section 12.
 * @param {{id: number, pseudo: string}} utilisateur
 * @returns {string} Le token signé.
 */
export function genererToken(utilisateur) {
  return jwt.sign({ id: utilisateur.id, pseudo: utilisateur.pseudo }, process.env.JWT_SECRET, {
    expiresIn: Math.floor(DUREE_SESSION_MS / 1000),
  });
}

/**
 * Vérifie et décode un JWT de session.
 * @param {string} token
 * @returns {{id: number, pseudo: string}} Le payload décodé.
 * @throws {Error} Si le token est invalide ou expiré (jsonwebtoken lève).
 */
export function verifierToken(token) {
  return jwt.verify(token, process.env.JWT_SECRET);
}
