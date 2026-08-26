// seed.js
// Peuple la BDD avec les données de dataset.json : un utilisateur de démo,
// une progression sauvegardée et un skin avec ses images, pour avoir de
// quoi tester l'API sans passer par les formulaires d'inscription/upload.
import sequelize from "../models/sequelize-client.js";
import { Utilisateur, Progression, Skin, ImageSkin } from "../models/index.js";
import argon2 from "argon2";
import data from "./dataset.json" with { type: "json" };

async function seed() {
  try {
    console.log("Synchronisation de la BDD...");
    // { force: true } supprime les tables puis les recrée : on repart d'une
    // base vide à chaque seed, pour ne jamais dupliquer les données.
    await sequelize.sync({ force: true });

    // ⚠️ On seed toujours les tables SANS relations AVANT les tables AVEC
    // relations, sinon les clés étrangères pointeraient vers des lignes qui
    // n'existent pas encore.

    // Utilisateur (aucune dépendance) — mot de passe haché avant insertion,
    // jamais stocké en clair (cf. section 10 de PROMPT-HEADER-CLAUDE.md).
    console.log("Seeding Utilisateur...");
    const demoUser = await Utilisateur.create({
      email: data.user.email,
      pseudo: data.user.pseudo,
      mot_de_passe_hash: await argon2.hash(data.user.password),
    });
    console.log(
      `   -> identifiants de test : email="${data.user.email}", password="${data.user.password}"`,
    );

    // Progressions (dépend de Utilisateur)
    console.log("Seeding Progressions...");
    const progressionsData = data.progressions.map((progression) => ({
      ...progression,
      utilisateur_id: demoUser.id,
    }));
    await Progression.bulkCreate(progressionsData);

    // Skins (dépend de Utilisateur)
    console.log("Seeding Skins...");
    for (const skinData of data.skins) {
      const skin = await Skin.create({
        nom_skin: skinData.nom_skin,
        utilisateur_id: demoUser.id,
      });

      // Images du skin (dépend de Skin)
      const imagesData = skinData.images.map((image) => ({
        ...image,
        skin_id: skin.id,
      }));
      await ImageSkin.bulkCreate(imagesData);
    }

    console.log("✅ Seed terminé !");
  } catch (error) {
    console.error("❌ Erreur pendant le seed :", error);
  } finally {
    await sequelize.close();
  }
}

seed();
