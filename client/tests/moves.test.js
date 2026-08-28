// Tests du moteur de mouvements (src/lib/moves.js). Deux familles bien
// distinctes, cf. commentaire de moves.js :
//
// - Propriétés ALGÉBRIQUES (ordre 4, inverse, conservation des couleurs) :
//   nécessaires mais PAS suffisantes pour garantir la fidélité à un vrai
//   cube physique — un mauvais câblage cohérent des adjacences passerait
//   quand même ces tests (une permutation à 4 cycles reste d'ordre 4
//   qu'elle soit "dans le bon sens" ou non).
// - Cas CONNUS/VÉRIFIÉS : quelques assertions précises correspondant à la
//   géométrie dérivée et recoupée avec une source externe (cf. moves.js
//   et le carnet de bord) — celles-ci vérifient la fidélité, pas
//   seulement la cohérence interne.
import { describe, it } from "node:test";
import assert from "node:assert";
import { creerCubeResolu, FACES, versEtatDepart } from "../src/lib/cube.js";
import {
  appliquerMouvement,
  appliquerSequence,
  inverserMouvement,
  inverserSequence,
  estResolu,
  melanger,
} from "../src/lib/moves.js";

const TOUS_LES_MOUVEMENTS = ["U", "D", "L", "R", "F", "B"].flatMap((face) => [
  face,
  `${face}'`,
  `${face}2`,
]);

describe("moteur de mouvements — propriétés algébriques (cohérence interne)", () => {
  it("un cube résolu est bien détecté comme résolu", () => {
    assert.equal(estResolu(creerCubeResolu()), true);
  });

  for (const mouvement of TOUS_LES_MOUVEMENTS) {
    it(`${mouvement} appliqué 4 fois revient à l'identité`, () => {
      let cube = creerCubeResolu();
      for (let i = 0; i < 4; i++) cube = appliquerMouvement(cube, mouvement);
      assert.deepEqual(cube, creerCubeResolu());
    });

    it(`${mouvement} puis son inverse (${inverserMouvement(mouvement)}) revient à l'identité`, () => {
      let cube = appliquerMouvement(creerCubeResolu(), mouvement);
      cube = appliquerMouvement(cube, inverserMouvement(mouvement));
      assert.deepEqual(cube, creerCubeResolu());
    });

    it(`${mouvement} sur un cube résolu le rend non résolu`, () => {
      // Sauf coïncidence impossible ici : aucun de ces 18 mouvements n'est
      // neutre sur un cube résolu.
      const cube = appliquerMouvement(creerCubeResolu(), mouvement);
      assert.equal(estResolu(cube), false);
    });

    it(`${mouvement} conserve 9 stickers de chaque couleur`, () => {
      const cube = appliquerMouvement(creerCubeResolu(), mouvement);
      const comptage = {};
      for (const face of FACES) {
        for (const couleur of cube[face]) {
          comptage[couleur] = (comptage[couleur] || 0) + 1;
        }
      }
      assert.deepEqual(
        Object.values(comptage).sort(),
        [9, 9, 9, 9, 9, 9],
      );
    });
  }

  it("X2 équivaut à appliquer X deux fois d'affilée", () => {
    for (const face of FACES) {
      const viaX2 = appliquerMouvement(creerCubeResolu(), `${face}2`);
      const viaDeuxX = appliquerMouvement(appliquerMouvement(creerCubeResolu(), face), face);
      assert.deepEqual(viaX2, viaDeuxX);
    }
  });

  it("un mélange puis sa séquence inverse revient exactement au cube de départ", () => {
    const depart = creerCubeResolu();
    const { cube: melange, mouvements } = melanger(depart, 30);
    const restaure = appliquerSequence(melange, inverserSequence(mouvements));
    assert.deepEqual(restaure, depart);
  });

  it("l'etat_depart d'un cube mélangé reste valide pour l'API (54 caractères, palette correcte)", () => {
    const { cube } = melanger(creerCubeResolu(), 40);
    const etat = versEtatDepart(cube);
    assert.equal(etat.length, 54);
    assert.match(etat, /^[BJROVL]{54}$/);
  });
});

describe("moteur de mouvements — cas connus vérifiés (fidélité géométrique)", () => {
  it("U (horaire) fait circuler les bandes F -> L -> B -> R -> F (recoupé avec scottbedard/cube)", () => {
    const cube = creerCubeResolu();
    cube.F[0] = "rouge"; // sticker distinctif sur la bande de F touchant U
    const apres = appliquerMouvement(cube, "U");
    assert.equal(apres.L[0], "rouge", "le sticker de F doit arriver sur L, pas sur R");
  });

  it("R (horaire) fait circuler les bandes U -> B -> D -> F -> U (dérivé par matrice de rotation)", () => {
    const cube = creerCubeResolu();
    cube.F[2] = "jaune"; // sticker distinctif sur la bande de F touchant R
    const apres = appliquerMouvement(cube, "R");
    assert.equal(apres.U[2], "jaune", "le sticker de F doit arriver sur U, pas sur D");
  });
});
