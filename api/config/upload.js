// Configuration multer pour l'upload des images de skin. Stockage en
// mémoire (pas sur disque directement) : le controller valide la couleur
// et l'appartenance du skin AVANT d'écrire quoi que ce soit sur le
// filesystem, pour ne jamais laisser un fichier orphelin en cas de rejet.
import multer from "multer";

// Types MIME acceptés et leur extension de sortie — évite de faire
// confiance au nom de fichier fourni par le client (jamais fiable).
export const EXTENSIONS_PAR_TYPE = {
  "image/png": ".png",
  "image/jpeg": ".jpg",
  "image/webp": ".webp",
};

const TAILLE_MAX_OCTETS = 5 * 1024 * 1024; // 5 Mo — large pour un sticker de cube

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: TAILLE_MAX_OCTETS },
  fileFilter(req, file, cb) {
    if (!Object.keys(EXTENSIONS_PAR_TYPE).includes(file.mimetype)) {
      cb(new Error("Format d'image non supporté (PNG, JPEG ou WebP uniquement)."));
      return;
    }
    cb(null, true);
  },
});

/**
 * Middleware factory : upload d'un seul fichier sur le champ donné, avec
 * les erreurs multer (type non supporté, fichier trop lourd) transformées
 * en réponse 400 propre au lieu de remonter au middleware d'erreur 500
 * générique (cf. section 13).
 * @param {string} champ - Nom du champ multipart contenant le fichier.
 */
export function uploadImageUnique(champ) {
  const middleware = upload.single(champ);
  return (req, res, next) => {
    middleware(req, res, (erreur) => {
      if (erreur) {
        return res.status(400).json({ message: erreur.message });
      }
      next();
    });
  };
}
