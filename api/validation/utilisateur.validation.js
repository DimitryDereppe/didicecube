// Schémas Joi pour les entrées liées aux comptes utilisateurs (cf. section 7).
// Le middleware de validation générique vit dans
// api/middlewares/validation.middleware.js (partagé par toutes les ressources).
import Joi from "joi";

export const schemaInscription = Joi.object({
  email: Joi.string().email().max(255).required(),
  pseudo: Joi.string().min(3).max(30).required(),
  // Pas de plafond artificiel bas (section 10) : 128 caractères autorisés.
  // Minimum 8 : compromis raisonnable pour un projet vitrine, pas une
  // politique de complexité intrusive (chiffres/majuscules obligatoires).
  mot_de_passe: Joi.string().min(8).max(128).required(),
});

// Connexion par pseudo (pas email) : plus simple à retenir/saisir pour
// l'utilisateur — l'email reste demandé à l'inscription (identifiant de
// contact), mais n'est pas requis pour se reconnecter ensuite.
export const schemaConnexion = Joi.object({
  pseudo: Joi.string().required(),
  mot_de_passe: Joi.string().required(),
});
