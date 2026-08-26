// Schémas Joi pour les entrées liées aux progressions sauvegardées.
import Joi from "joi";

// 54 caractères, chacun parmi les 6 couleurs standards (cf. dictionnaire de
// données, api/docs/06-dictionnaire-de-donnees.md).
const REGEX_ETAT_CUBE = /^[BJROVL]{54}$/;

export const schemaCreationProgression = Joi.object({
  etat_depart: Joi.string().pattern(REGEX_ETAT_CUBE).required().messages({
    "string.pattern.base":
      "L'état du cube doit être une chaîne de 54 caractères parmi B/J/R/O/V/L.",
  }),
  etape_courante: Joi.number().integer().min(0).default(0),
});

export const schemaMiseAJourProgression = Joi.object({
  etape_courante: Joi.number().integer().min(0).required(),
});
