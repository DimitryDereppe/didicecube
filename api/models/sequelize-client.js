// Instance Sequelize partagée par tous les modèles — connexion à la BDD
// PostgreSQL, configurée via les variables d'environnement (cf. .env.example).
// Aucune logique métier ici : uniquement la configuration de la connexion.

import "dotenv/config";
import { Sequelize } from "sequelize";

const sequelize = new Sequelize(
  process.env.PGDATABASE,
  process.env.PGUSER,
  process.env.PGPASSWORD,
  {
    host: process.env.PGHOST,
    port: process.env.PGPORT,
    dialect: "postgres",
    // Logs SQL desactives par defaut : trop verbeux en usage normal, a
    // remettre a `console.log` ponctuellement pour debugger une requete.
    logging: false,
  },
);

export default sequelize;
