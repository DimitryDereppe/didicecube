// Tests unitaires : api/services/auth.service.js — uniquement des
// fonctions pures/cryptographiques, aucune BDD ni serveur nécessaire
// (cf. SB08, node:test + node:assert).
import { describe, it } from "node:test";
import assert from "node:assert";
import "dotenv/config";
import {
  hacherMotDePasse,
  verifierMotDePasse,
  genererToken,
  verifierToken,
} from "../services/auth.service.js";

describe("auth.service — mots de passe (Argon2)", () => {
  it("un mot de passe haché puis vérifié avec la bonne valeur est reconnu", async () => {
    const hash = await hacherMotDePasse("MotDePasse123");
    assert.equal(await verifierMotDePasse(hash, "MotDePasse123"), true);
  });

  it("un mauvais mot de passe est rejeté", async () => {
    const hash = await hacherMotDePasse("MotDePasse123");
    assert.equal(await verifierMotDePasse(hash, "UnAutreMotDePasse"), false);
  });

  it("le hash ne contient jamais le mot de passe en clair (section 12)", async () => {
    const hash = await hacherMotDePasse("MotDePasse123");
    assert.equal(hash.includes("MotDePasse123"), false);
  });
});

describe("auth.service — JWT", () => {
  const utilisateurFictif = { id: 42, pseudo: "testeur" };

  it("un token généré se décode avec les mêmes id/pseudo", () => {
    const token = genererToken(utilisateurFictif);
    const payload = verifierToken(token);
    assert.equal(payload.id, utilisateurFictif.id);
    assert.equal(payload.pseudo, utilisateurFictif.pseudo);
  });

  it("le payload ne contient jamais de donnée sensible (section 12)", () => {
    const token = genererToken(utilisateurFictif);
    const payload = verifierToken(token);
    assert.equal(payload.mot_de_passe_hash, undefined);
  });

  it("un token invalide/malformé est rejeté", () => {
    assert.throws(() => verifierToken("token.invalide.xyz"));
  });
});
