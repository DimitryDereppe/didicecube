// Modèle Sequelize : image d'un skin, associée à une des 6 couleurs
// standards du cube qu'elle remplace visuellement.
import { DataTypes } from "sequelize";
import sequelize from "./sequelize-client.js";

// Les 6 couleurs standards du cube qu'une image de skin peut remplacer.
export const COULEURS_CUBE = ["blanc", "jaune", "rouge", "orange", "vert", "bleu"];

const ImageSkin = sequelize.define(
  "ImageSkin",
  {
    couleur: {
      type: DataTypes.ENUM(...COULEURS_CUBE),
      allowNull: false,
    },
    chemin_fichier: {
      type: DataTypes.STRING,
      allowNull: false,
    },
  },
  {
    tableName: "image_skin",
    timestamps: false,
    indexes: [
      // Un skin ne peut pas avoir deux images pour la même couleur
      // (cf. règle de gestion, 04-relations-cardinalites.md).
      { unique: true, fields: ["skin_id", "couleur"] },
    ],
  },
);

export default ImageSkin;
