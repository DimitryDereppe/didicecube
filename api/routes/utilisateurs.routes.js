// Route : ressource /utilisateurs — définition des endpoints uniquement,
// aucune logique ici (cf. section 3, SoC).
import { Router } from "express";
import { inscrire, recupererUtilisateurConnecte } from "../controllers/utilisateurs.controller.js";
import { schemaInscription } from "../validation/utilisateur.validation.js";
import { valider } from "../middlewares/validation.middleware.js";
import { protegerRoute } from "../middlewares/auth.middleware.js";

const router = Router();

router.post("/", valider(schemaInscription), inscrire);
router.get("/moi", protegerRoute, recupererUtilisateurConnecte);

export default router;
