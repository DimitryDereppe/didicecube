// Modèle Sequelize : progression de résolution sauvegardée par un
// utilisateur (état de départ du cube + étape atteinte).
import { DataTypes } from "sequelize";
import sequelize from "./sequelize-client.js";

const Progression = sequelize.define(
  "Progression",
  {
    // État de départ du cube : une chaîne de 54 caractères, un par sticker,
    // chacun parmi les 6 couleurs standards (cf. dictionnaire de données).
    etat_depart: {
      type: DataTypes.STRING(54),
      allowNull: false,
      validate: {
        is: /^[BJROVL]{54}$/, // 54 lettres parmi Blanc/Jaune/Rouge/Orange/Vert/bLeu
      },
    },
    // Index du mouvement où l'utilisateur s'est arrêté — pas la liste des
    // mouvements elle-même, recalculée par l'algorithme depuis etat_depart
    // (donnée dérivable, non stockée, cf. dictionnaire de données).
    etape_courante: {
      type: DataTypes.INTEGER,
      allowNull: false,
      defaultValue: 0,
      validate: { min: 0 },
    },
    date_creation: {
      type: DataTypes.DATE,
      allowNull: false,
      defaultValue: DataTypes.NOW,
    },
    date_maj: {
      type: DataTypes.DATE,
      allowNull: false,
      defaultValue: DataTypes.NOW,
    },
  },
  {
    tableName: "progression",
    timestamps: false,
  },
);

export default Progression;
