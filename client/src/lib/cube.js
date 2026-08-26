// État du cube (6 faces × 9 stickers) et conversions liées — donnée
// d'application transitoire, pas de BDD tant qu'elle n'est pas sauvegardée
// explicitement en progression (cf. CLAUDE.md, "pas de BDD pour l'état du
// cube en cours de résolution"). Représentation en mémoire ici, convertie
// en chaîne de 54 caractères pour l'API (etat_depart) au moment de la
// sauvegarde.

// Ordre des faces dans la chaîne etat_depart de l'API (cf.
// api/docs/06-dictionnaire-de-donnees.md) : U, D, L, R, F, B.
export const FACES = ["U", "D", "L", "R", "F", "B"];

export const NOMS_FACES = {
  U: "Dessus",
  D: "Dessous",
  L: "Gauche",
  R: "Droite",
  F: "Face avant",
  B: "Face arrière",
};

// Couleur affichée (hex) + code envoyé à l'API pour chaque couleur standard
// (cf. dictionnaire de données : B/J/R/O/V/L).
export const COULEURS = {
  blanc: { code: "B", hex: "#ffffff", libelle: "Blanc" },
  jaune: { code: "J", hex: "#ffd500", libelle: "Jaune" },
  rouge: { code: "R", hex: "#c41e1e", libelle: "Rouge" },
  orange: { code: "O", hex: "#ff8c00", libelle: "Orange" },
  vert: { code: "V", hex: "#009e26", libelle: "Vert" },
  bleu: { code: "L", hex: "#0051ba", libelle: "Bleu" },
};

// Face du cube résolu -> couleur (schéma occidental standard : blanc/jaune,
// orange/rouge, vert/bleu sont les paires de faces opposées).
const COULEUR_PAR_FACE_RESOLUE = {
  U: "blanc",
  D: "jaune",
  L: "orange",
  R: "rouge",
  F: "vert",
  B: "bleu",
};

/** Crée un état de cube résolu (une seule couleur par face). */
export function creerCubeResolu() {
  const cube = {};
  for (const face of FACES) {
    cube[face] = Array(9).fill(COULEUR_PAR_FACE_RESOLUE[face]);
  }
  return cube;
}

/**
 * Convertit l'état en mémoire en chaîne de 54 caractères attendue par
 * l'API (POST /progressions, champ etat_depart).
 */
export function versEtatDepart(cube) {
  return FACES.map((face) => cube[face].map((couleur) => COULEURS[couleur].code).join("")).join(
    "",
  );
}

// Inverse de COULEURS[x].code -> x, pour reconstruire un état en mémoire
// depuis la chaîne stockée en base (ex. en rechargeant une progression).
const COULEUR_PAR_CODE = Object.fromEntries(
  Object.entries(COULEURS).map(([nom, info]) => [info.code, nom]),
);

/**
 * Convertit une chaîne de 54 caractères (etat_depart, venant de l'API) en
 * état de cube en mémoire — inverse de versEtatDepart().
 */
export function depuisEtatDepart(chaine) {
  const cube = {};
  FACES.forEach((face, i) => {
    cube[face] = chaine
      .slice(i * 9, i * 9 + 9)
      .split("")
      .map((code) => COULEUR_PAR_CODE[code]);
  });
  return cube;
}
