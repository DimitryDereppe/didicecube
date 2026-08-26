// Fichier pour synchroniser les classes du modèle (JS) avec la BDD.
// La BDD est construite à partir des modèles Sequelize définis en JS
// (api/models/), qui sont la seule source de vérité du schéma physique —
// il n'y a pas de script SQL indicatif à traduire pour ce projet.

import "dotenv/config";
import sequelize from "../models/sequelize-client.js";
import "../models/index.js"; // important : enregistre les modèles et leurs associations

async function syncDb() {
  try {
    // { alter: true } compare l'état actuel de la BDD avec les modèles et
    // applique les changements nécessaires. Pratique en développement,
    // mais à ne jamais faire en production (risque de perte de données).
    await sequelize.sync({ alter: true });
    console.log("✅ Base de données synchronisée avec succès !");
  } catch (error) {
    console.error("❌ Erreur lors de la synchronisation de la base :", error);
  } finally {
    await sequelize.close();
  }
}

syncDb();
