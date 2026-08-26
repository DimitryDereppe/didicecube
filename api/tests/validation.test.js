// Tests unitaires : schémas Joi (api/validation/) — aucune BDD ni serveur
// nécessaire, uniquement schema.validate() sur des objets en mémoire.
import { describe, it } from "node:test";
import assert from "node:assert";
import { schemaInscription, schemaConnexion } from "../validation/utilisateur.validation.js";
import {
  schemaCreationProgression,
  schemaMiseAJourProgression,
} from "../validation/progression.validation.js";

const ETAT_CUBE_VALIDE = "BJROVL".repeat(9); // 54 caractères, palette valide

describe("validation — utilisateur (inscription/connexion)", () => {
  it("accepte une inscription valide", () => {
    const { error } = schemaInscription.validate({
      email: "test@example.com",
      pseudo: "testeur",
      mot_de_passe: "MotDePasse123",
    });
    assert.equal(error, undefined);
  });

  it("refuse un email invalide", () => {
    const { error } = schemaInscription.validate({
      email: "pas-un-email",
      pseudo: "testeur",
      mot_de_passe: "MotDePasse123",
    });
    assert.ok(error);
  });

  it("refuse un mot de passe trop court (< 8 caractères)", () => {
    const { error } = schemaInscription.validate({
      email: "test@example.com",
      pseudo: "testeur",
      mot_de_passe: "court",
    });
    assert.ok(error);
  });

  it("connexion : email et mot de passe sont tous les deux requis", () => {
    // { abortEarly: false } : mêmes options que le middleware valider()
    // réellement utilisé par les routes (cf. validation.middleware.js),
    // sinon Joi s'arrête à la première erreur par défaut.
    const { error } = schemaConnexion.validate({}, { abortEarly: false });
    assert.ok(error);
    assert.equal(error.details.length, 2);
  });
});

describe("validation — progression", () => {
  it("accepte un état de cube valide (54 caractères de la palette)", () => {
    const { error, value } = schemaCreationProgression.validate({
      etat_depart: ETAT_CUBE_VALIDE,
    });
    assert.equal(error, undefined);
    assert.equal(value.etape_courante, 0); // valeur par défaut appliquée par Joi
  });

  it("refuse un état de cube trop court", () => {
    const { error } = schemaCreationProgression.validate({ etat_depart: "BJR" });
    assert.ok(error);
  });

  it("refuse un caractère hors palette (ex. X, absent de B/J/R/O/V/L)", () => {
    const { error } = schemaCreationProgression.validate({ etat_depart: "X".repeat(54) });
    assert.ok(error);
  });

  it("mise à jour : etape_courante doit être un entier positif ou nul", () => {
    const { error } = schemaMiseAJourProgression.validate({ etape_courante: -1 });
    assert.ok(error);
  });

  it("mise à jour : etape_courante est requis", () => {
    const { error } = schemaMiseAJourProgression.validate({});
    assert.ok(error);
  });
});
