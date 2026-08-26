// Route : ressource /skins — entièrement protégée par l'authentification.
import { Router } from "express";
import {
  creer,
  lister,
  recuperer,
  supprimer,
  ajouterImage,
  supprimerImage,
} from "../controllers/skins.controller.js";
import { schemaCreationSkin, schemaAjoutImage } from "../validation/skin.validation.js";
import { valider, validerIdNumerique } from "../middlewares/validation.middleware.js";
import { protegerRoute } from "../middlewares/auth.middleware.js";
import { uploadImageUnique } from "../config/upload.js";

const router = Router();

router.use(protegerRoute);

router.post("/", valider(schemaCreationSkin), creer);
router.get("/", lister);
router.get("/:id", validerIdNumerique(), recuperer);
router.delete("/:id", validerIdNumerique(), supprimer);

// multipart/form-data : multer (uploadImageUnique) doit tourner AVANT
// valider(), sinon req.body (champ "couleur") n'est pas encore peuplé.
router.post(
  "/:id/images",
  validerIdNumerique(),
  uploadImageUnique("image"),
  valider(schemaAjoutImage),
  ajouterImage,
);
router.delete("/:id/images/:couleur", validerIdNumerique(), supprimerImage);

export default router;
