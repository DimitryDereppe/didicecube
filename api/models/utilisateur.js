// Modèle Sequelize : compte utilisateur (email/pseudo + mot de passe haché).
import { DataTypes } from "sequelize";
import sequelize from "./sequelize-client.js";

const Utilisateur = sequelize.define(
  "Utilisateur",
  {
    email: {
      type: DataTypes.STRING,
      allowNull: false,
      unique: true,
      validate: { isEmail: true },
    },
    pseudo: {
      type: DataTypes.STRING,
      allowNull: false,
      unique: true,
    },
    // Jamais le mot de passe en clair : uniquement son hash Argon2 (cf.
    // section 10 de PROMPT-HEADER-CLAUDE.md). Le hachage se fait dans le
    // Service, avant l'appel à Utilisateur.create()/update().
    mot_de_passe_hash: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    date_inscription: {
      type: DataTypes.DATE,
      allowNull: false,
      defaultValue: DataTypes.NOW,
    },
  },
  {
    tableName: "utilisateur",
    timestamps: false, // date_inscription joue déjà ce rôle
  },
);

export default Utilisateur;
