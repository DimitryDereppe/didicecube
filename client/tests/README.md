# Tests — Didicecube client

Tests unitaires (`node:test`, natif) de la logique **pure** du client — pas
de composant Svelte ni de DOM ici, uniquement `src/lib/cube.js` et
`src/lib/moves.js`.

```bash
npm test
```

## `moves.test.js` — moteur de mouvements

Deux familles de tests, à ne pas confondre (cf. le commentaire en tête de
`src/lib/moves.js`) :

- **Propriétés algébriques** (ordre 4, inverse, conservation des couleurs) :
  vérifient que le moteur est **cohérent avec lui-même**, mais ne prouvent
  pas qu'il correspond à un vrai cube physique — une adjacence des faces
  mal câblée mais cohérente passerait quand même ces tests.
- **Cas connus vérifiés** : quelques assertions précises (ex. « U fait
  passer un sticker de F vers L ») qui correspondent à une géométrie
  dérivée par calcul vectoriel et recoupée avec une bibliothèque externe de
  référence (cf. carnet de bord, entrée sur la recherche de l'algorithme de
  résolution) — celles-ci vérifient la fidélité à un cube réel.

⚠️ Le rendu 3D du cube n'a jamais pu être vérifié visuellement dans
l'environnement de développement utilisé pour écrire ce moteur (pas de
navigateur disponible) — une vérification visuelle reste la validation la
plus fiable, à faire dès que possible.
