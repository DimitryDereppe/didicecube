// Point d'entrée des modèles : importe chaque modèle et déclare les
// associations entre eux. Sequelize a besoin que ce fichier soit chargé une
// fois (import pour effet de bord) pour enregistrer les clés étrangères
// avant tout sequelize.sync() — cf. api/migrations/01.create-tables.js.
import Utilisateur from "./utilisateur.js";
import Progression from "./progression.js";
import Skin from "./skin.js";
import ImageSkin from "./image-skin.js";

// Toutes les associations du projet sont des 1,1 — 0,n : le côté "1,1"
// porte une clé étrangère OBLIGATOIRE (allowNull: false, cf. cardinalité,
// 04-relations-cardinalites.md) et la suppression du parent supprime les
// enfants en cascade (onDelete: "CASCADE") plutôt que de laisser une clé
// étrangère obligatoire passer à NULL (comportement par défaut de
// Sequelize, incompatible avec allowNull: false).
//
// Alias (`as`) explicites sur chaque association : évite de dépendre de la
// pluralisation automatique de Sequelize (fragile, magique) dès qu'on fait
// un include (ex. Skin.findAll({ include: "images" })).

// UTILISATEUR (0,n) — POSSEDER — (1,1) PROGRESSION
Utilisateur.hasMany(Progression, {
  as: "progressions",
  foreignKey: { name: "utilisateur_id", allowNull: false },
  onDelete: "CASCADE",
});
Progression.belongsTo(Utilisateur, {
  as: "utilisateur",
  foreignKey: { name: "utilisateur_id", allowNull: false },
});

// UTILISATEUR (0,n) — TELECHARGER — (1,1) SKIN
Utilisateur.hasMany(Skin, {
  as: "skins",
  foreignKey: { name: "utilisateur_id", allowNull: false },
  onDelete: "CASCADE",
});
Skin.belongsTo(Utilisateur, {
  as: "utilisateur",
  foreignKey: { name: "utilisateur_id", allowNull: false },
});

// SKIN (0,n) — COMPOSER — (1,1) IMAGE_SKIN
Skin.hasMany(ImageSkin, {
  as: "images",
  foreignKey: { name: "skin_id", allowNull: false },
  onDelete: "CASCADE",
});
ImageSkin.belongsTo(Skin, {
  as: "skin",
  foreignKey: { name: "skin_id", allowNull: false },
});

export { Utilisateur, Progression, Skin, ImageSkin };
