// Schémas Joi pour les entrées liées aux skins et à leurs images.
import Joi from "joi";
import { COULEURS_CUBE } from "../models/image-skin.js";

export const schemaCreationSkin = Joi.object({
  nom_skin: Joi.string().min(1).max(60).required(),
});

// Le fichier lui-même est validé par multer (config/upload.js) : ce schéma
// ne couvre que le champ texte "couleur" du même formulaire multipart.
export const schemaAjoutImage = Joi.object({
  couleur: Joi.string()
    .valid(...COULEURS_CUBE)
    .required(),
});
