// Middleware transverse générique : valide req.body contre un schéma Joi
// donné (cf. section 7 : valider/assainir toutes les entrées avant tout
// traitement). Partagé par toutes les ressources, indépendant du métier.
/**
 * Middleware factory : valide req.body contre un schéma Joi. Répond 400
 * avec le détail des erreurs si la validation échoue ; sinon remplace
 * req.body par la version validée (défauts Joi appliqués, ex.
 * etape_courante = 0) et passe la main.
 * @param {import("joi").ObjectSchema} schema
 */
export function valider(schema) {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.body, { abortEarly: false });
    if (error) {
      return res.status(400).json({
        message: "Données invalides.",
        details: error.details.map((detail) => detail.message),
      });
    }
    req.body = value;
    next();
  };
}

/**
 * Middleware : vérifie que req.params[nomParametre] est un entier positif
 * avant d'atteindre le controller — sinon une requête SQL avec un id
 * non numérique (ex. /progressions/abc) remonterait une erreur de la BDD
 * plutôt qu'une réponse propre (cf. section 13, l'API ne doit jamais
 * crasher sur une donnée absente/invalide).
 * @param {string} nomParametre - Nom du paramètre de route (ex. "id").
 */
export function validerIdNumerique(nomParametre = "id") {
  return (req, res, next) => {
    if (!/^\d+$/.test(req.params[nomParametre])) {
      return res.status(400).json({ message: `Paramètre "${nomParametre}" invalide.` });
    }
    next();
  };
}
