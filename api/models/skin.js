// Modèle Sequelize : skin (habillage visuel du cube) téléchargé par un
// utilisateur.
import { DataTypes } from "sequelize";
import sequelize from "./sequelize-client.js";

const Skin = sequelize.define(
  "Skin",
  {
    nom_skin: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    date_ajout: {
      type: DataTypes.DATE,
      allowNull: false,
      defaultValue: DataTypes.NOW,
    },
  },
  {
    tableName: "skin",
    timestamps: false,
  },
);

export default Skin;
