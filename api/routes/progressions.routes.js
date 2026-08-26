// Route : ressource /progressions — entièrement protégée par
// l'authentification (un visiteur non connecté n'a pas de progression
// sauvegardée, cf. CLAUDE.md).
import { Router } from "express";
import {
  creer,
  lister,
  recuperer,
  mettreAJour,
  supprimer,
} from "../controllers/progressions.controller.js";
import {
  schemaCreationProgression,
  schemaMiseAJourProgression,
} from "../validation/progression.validation.js";
import { valider, validerIdNumerique } from "../middlewares/validation.middleware.js";
import { protegerRoute } from "../middlewares/auth.middleware.js";

const router = Router();

router.use(protegerRoute);

router.post("/", valider(schemaCreationProgression), creer);
router.get("/", lister);
router.get("/:id", validerIdNumerique(), recuperer);
router.patch("/:id", validerIdNumerique(), valider(schemaMiseAJourProgression), mettreAJour);
router.delete("/:id", validerIdNumerique(), supprimer);

export default router;
