// Route : ressource /sessions (connexion = créer une session, déconnexion
// = supprimer la session) — définition des endpoints uniquement.
import { Router } from "express";
import { connecter, deconnecter } from "../controllers/sessions.controller.js";
import { schemaConnexion } from "../validation/utilisateur.validation.js";
import { valider } from "../middlewares/validation.middleware.js";

const router = Router();

router.post("/", valider(schemaConnexion), connecter);
router.delete("/", deconnecter);

export default router;
