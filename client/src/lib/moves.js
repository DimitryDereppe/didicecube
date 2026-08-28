// Moteur de mouvements du cube : applique les 18 mouvements de base
// (U/U'/U2, D/D'/D2, L/L'/L2, R/R'/R2, F/F'/F2, B/B'/B2) à un état de cube
// en mémoire (cf. cube.js pour la représentation {U,D,L,R,F,B: [9 couleurs]}).
//
// Convention géométrique : chaque face est indexée 0..8, de haut en bas et
// de gauche à droite, TELLE QUE VUE DE L'EXTÉRIEUR DU CUBE en la regardant
// de face. Le repère (droite, haut) de chaque face est choisi pour former
// un repère direct avec la normale sortante de la face (même principe que
// les "cube maps" en infographie 3D) — ce choix fait que les bandes de
// stickers adjacentes entre deux faces voisines se correspondent toujours
// dans le MÊME ordre, sans jamais avoir besoin de les inverser.
//
// Dérivé à la main par calcul vectoriel (produit vectoriel pour
// l'adjacence, matrices de rotation pour vérifier chaque face
// indépendamment — les deux méthodes se recoupent) et recoupé avec le sens
// de rotation du mouvement U documenté par la bibliothèque de référence
// scottbedard/cube (github.com/scottbedard/cube) : le cube en cours
// d'écriture n'utilise aucun code de cette bibliothèque, seulement le fait
// géométrique qu'elle documente (U horaire fait circuler les bandes selon
// F → L → B → R → F).
//
// FIABILITÉ : cette géométrie est vérifiée par le calcul et recoupée avec
// une source externe, mais jamais vue tourner dans un vrai cube 3D affiché
// (aucun navigateur disponible dans cet environnement de développement) —
// une vérification visuelle reste utile dès que possible (cf. carnet de
// bord). Les tests de moves.test.js vérifient la cohérence interne
// (propriétés algébriques : ordre 4, inverse, conservation des couleurs)
// et incluent des cas précis correspondant à la géométrie ci-dessus — mais
// seule une vérification visuelle confirmerait la fidélité à un cube réel.

import { FACES } from "./cube.js";

// Rotation propre d'une face (ses 9 stickers), sens horaire vu de l'extérieur :
// new[i] = old[ROTATION_PROPRE_HORAIRE[i]].
const ROTATION_PROPRE_HORAIRE = [6, 3, 0, 7, 4, 1, 8, 5, 2];

// Pour chaque face, ses 4 bandes de stickers voisines dans l'ordre
// [haut, droite, bas, gauche] (sens horaire, vu de l'extérieur de la
// face). Un tour horaire fait "avancer" chaque bande d'une position dans
// cette liste (ex. pour F : la bande de gauche — sur L — devient la
// nouvelle bande du haut — sur U).
const BANDES_VOISINES = {
  F: [
    { face: "U", index: [6, 7, 8] },
    { face: "R", index: [0, 3, 6] },
    { face: "D", index: [0, 1, 2] },
    { face: "L", index: [2, 5, 8] },
  ],
  U: [
    { face: "B", index: [0, 1, 2] },
    { face: "R", index: [0, 1, 2] },
    { face: "F", index: [0, 1, 2] },
    { face: "L", index: [0, 1, 2] },
  ],
  D: [
    { face: "F", index: [6, 7, 8] },
    { face: "R", index: [6, 7, 8] },
    { face: "B", index: [6, 7, 8] },
    { face: "L", index: [6, 7, 8] },
  ],
  R: [
    { face: "U", index: [2, 5, 8] },
    { face: "B", index: [0, 3, 6] },
    { face: "D", index: [2, 5, 8] },
    { face: "F", index: [2, 5, 8] },
  ],
  L: [
    { face: "U", index: [0, 3, 6] },
    { face: "F", index: [0, 3, 6] },
    { face: "D", index: [0, 3, 6] },
    { face: "B", index: [2, 5, 8] },
  ],
  B: [
    { face: "U", index: [0, 1, 2] },
    { face: "L", index: [0, 3, 6] },
    { face: "D", index: [6, 7, 8] },
    { face: "R", index: [2, 5, 8] },
  ],
};

function lireBande(cube, { face, index }) {
  return index.map((i) => cube[face][i]);
}

function ecrireBande(cube, { face, index }, valeurs) {
  index.forEach((i, k) => {
    cube[face][i] = valeurs[k];
  });
}

function copierCube(cube) {
  const copie = {};
  for (const face of FACES) copie[face] = [...cube[face]];
  return copie;
}

/**
 * Applique un quart de tour horaire (vu de l'extérieur) à une face donnée.
 * Ne modifie jamais le cube reçu — renvoie un nouvel état.
 * @param {object} cube
 * @param {"U"|"D"|"L"|"R"|"F"|"B"} face
 */
function tournerHoraire(cube, face) {
  const nouveau = copierCube(cube);

  nouveau[face] = ROTATION_PROPRE_HORAIRE.map((i) => cube[face][i]);

  const bandes = BANDES_VOISINES[face];
  const [haut, droite, bas, gauche] = bandes.map((bande) => lireBande(cube, bande));
  ecrireBande(nouveau, bandes[0], gauche); // nouveau haut = ancien gauche
  ecrireBande(nouveau, bandes[1], haut); // nouveau droite = ancien haut
  ecrireBande(nouveau, bandes[2], droite); // nouveau bas = ancien droite
  ecrireBande(nouveau, bandes[3], bas); // nouveau gauche = ancien bas

  return nouveau;
}

/**
 * Applique un mouvement en notation standard ("U", "U'", "U2", "D", ...) à
 * un état de cube. Les variantes ' (anti-horaire) et 2 (demi-tour) sont
 * dérivées en répétant le quart de tour horaire (3 fois, 2 fois) plutôt
 * que ré-implémentées séparément : garantit par construction que 4 tours
 * reviennent à l'identité et que X' est bien l'inverse de X, sans code
 * supplémentaire à faire confiance.
 * @param {object} cube
 * @param {string} mouvement
 */
export function appliquerMouvement(cube, mouvement) {
  const face = mouvement[0];
  const suffixe = mouvement.slice(1);
  const repetitions = suffixe === "'" ? 3 : suffixe === "2" ? 2 : 1;

  let resultat = cube;
  for (let i = 0; i < repetitions; i++) {
    resultat = tournerHoraire(resultat, face);
  }
  return resultat;
}

/** Applique une séquence de mouvements dans l'ordre. */
export function appliquerSequence(cube, mouvements) {
  return mouvements.reduce((etat, mvt) => appliquerMouvement(etat, mvt), cube);
}

/** Inverse d'un mouvement isolé : U <-> U', U2 reste U2. */
export function inverserMouvement(mouvement) {
  if (mouvement.endsWith("'")) return mouvement.slice(0, -1);
  if (mouvement.endsWith("2")) return mouvement;
  return `${mouvement}'`;
}

/** Inverse d'une séquence : ordre inversé, chaque mouvement inversé. */
export function inverserSequence(mouvements) {
  return [...mouvements].reverse().map(inverserMouvement);
}

/** Un cube est résolu si chaque face n'a qu'une seule couleur. */
export function estResolu(cube) {
  return FACES.every((face) => cube[face].every((couleur) => couleur === cube[face][0]));
}

const SUFFIXES = ["", "'", "2"];

/**
 * Mélange un cube avec des mouvements aléatoires — utile pour les tests et
 * pour une future fonctionnalité "mélanger mon cube" côté interface.
 * @returns {{cube: object, mouvements: string[]}}
 */
export function melanger(cube, nombreDeMouvements = 20) {
  const mouvements = [];
  let resultat = cube;
  for (let i = 0; i < nombreDeMouvements; i++) {
    const face = FACES[Math.floor(Math.random() * FACES.length)];
    const suffixe = SUFFIXES[Math.floor(Math.random() * SUFFIXES.length)];
    const mouvement = face + suffixe;
    mouvements.push(mouvement);
    resultat = appliquerMouvement(resultat, mouvement);
  }
  return { cube: resultat, mouvements };
}
