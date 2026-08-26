// Point d'entrée de l'API Express : configuration des middlewares globaux,
// montage des routes, gestion des erreurs. Aucune logique métier ici
// (cf. section 3, SoC — elle vit dans les controllers/services).
import "dotenv/config";
import express from "express";
import cors from "cors";
import cookieParser from "cookie-parser";
import { xss } from "express-xss-sanitizer";

import "./models/index.js"; // charge les associations Sequelize (effet de bord)

import utilisateursRoutes from "./routes/utilisateurs.routes.js";
import sessionsRoutes from "./routes/sessions.routes.js";
import progressionsRoutes from "./routes/progressions.routes.js";
import skinsRoutes from "./routes/skins.routes.js";
import { routeIntrouvable, gererErreur } from "./middlewares/gestion-erreurs.middleware.js";

const app = express();

app.use(
  cors({
    // Origine du client Vite en dev ; à surcharger en prod via CLIENT_ORIGIN
    // (même domaine qu'Aldebaran, cf. CLAUDE.md).
    origin: process.env.CLIENT_ORIGIN || "http://localhost:5173",
    credentials: true, // nécessaire pour que le cookie httpOnly circule cross-origin
  }),
);
app.use(express.json());
app.use(cookieParser());
app.use(xss()); // nettoie body/params/query contre le XSS (cf. section 8bis)

// Fichiers uploadés (skins, photos de face du cube) servis tels quels :
// contenu public par nature (habillage visuel du cube), pas besoin d'être
// connecté pour les afficher.
app.use("/uploads", express.static(process.env.UPLOAD_DIR || "uploads"));

app.use("/utilisateurs", utilisateursRoutes);
app.use("/sessions", sessionsRoutes);
app.use("/progressions", progressionsRoutes);
app.use("/skins", skinsRoutes);

// Toujours en dernier : 404 puis 500 (cf. section 13).
app.use(routeIntrouvable);
app.use(gererErreur);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`API Didicecube à l'écoute sur le port ${PORT}`);
});

export default app;
