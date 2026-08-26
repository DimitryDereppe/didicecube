<script>
  // Cube 3D en CSS pur (transform-style: preserve-3d) — pas de librairie
  // externe type Three.js, cf. CLAUDE.md. Purement présentationnel : état du
  // cube, face active et couleur sélectionnée sont fournis par le parent.
  //
  // Accessibilité : seuls les stickers de la face active (celle tournée
  // vers l'écran) sont dans l'ordre de tabulation et exposés aux
  // lecteurs d'écran — les autres reçoivent tabindex="-1" et
  // aria-hidden="true", sinon le clavier traverserait 54 boutons dont 45
  // invisibles à un instant donné (cf. section 1, ordre de tabulation
  // logique).
  import { FACES, NOMS_FACES, COULEURS } from "../cube.js";

  // Rotation du groupe nécessaire pour amener chaque face bien en face de
  // la caméra : l'inverse de la transformation propre de cette face
  // (cf. règles CSS ci-dessous, en miroir de celles du <style>).
  const ROTATION_POUR_FACE = {
    F: { x: 0, y: 0 },
    B: { x: 0, y: 180 },
    U: { x: -90, y: 0 },
    D: { x: 90, y: 0 },
    R: { x: 0, y: -90 },
    L: { x: 0, y: 90 },
  };

  // Léger décalage esthétique en plus de l'alignement exact, pour que le
  // cube garde un aspect "3D" (on aperçoit un bout des faces voisines)
  // plutôt qu'un carré plat.
  const INCLINAISON = { x: -12, y: -18 };

  let { cube, faceActive, couleurSelectionnee, onStickerClick } = $props();

  let rotationX = $derived(ROTATION_POUR_FACE[faceActive].x + INCLINAISON.x);
  let rotationY = $derived(ROTATION_POUR_FACE[faceActive].y + INCLINAISON.y);
</script>

<div class="scene">
  <div class="cube" style="transform: rotateX({rotationX}deg) rotateY({rotationY}deg);">
    {#each FACES as face (face)}
      {@const active = face === faceActive}
      <div class="face face-{face}" class:active>
        {#each cube[face] as couleur, index (index)}
          <button
            type="button"
            class="sticker"
            style="background-color: {COULEURS[couleur].hex};"
            tabindex={active ? 0 : -1}
            aria-hidden={active ? undefined : "true"}
            aria-label={`${NOMS_FACES[face]}, sticker ${index + 1} sur 9, couleur ${COULEURS[couleur].libelle}. Cliquer pour appliquer : ${COULEURS[couleurSelectionnee].libelle}.`}
            onclick={() => onStickerClick(face, index)}
          ></button>
        {/each}
      </div>
    {/each}
  </div>
</div>

<style>
  .scene {
    perspective: 800px;
    display: flex;
    justify-content: center;
    padding: 2rem 0;
  }

  .cube {
    width: 180px;
    height: 180px;
    position: relative;
    margin: 0 auto;
    transform-style: preserve-3d;
    transition: transform 0.35s ease;
  }

  .face {
    position: absolute;
    width: 180px;
    height: 180px;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(3, 1fr);
    gap: 3px;
    padding: 3px;
    background: #1a1a1a;
    backface-visibility: hidden;
  }

  /* Seule la face active peut recevoir des clics — les autres sont, à un
     instant donné, tournées hors de vue (cf. backface-visibility ci-dessus) ;
     pointer-events: none en garde-fou supplémentaire. */
  .face:not(.active) {
    pointer-events: none;
  }

  .face-U { transform: rotateX(90deg) translateZ(90px); }
  .face-D { transform: rotateX(-90deg) translateZ(90px); }
  .face-F { transform: translateZ(90px); }
  .face-B { transform: rotateY(180deg) translateZ(90px); }
  .face-R { transform: rotateY(90deg) translateZ(90px); }
  .face-L { transform: rotateY(-90deg) translateZ(90px); }

  .sticker {
    border: 1px solid rgba(0, 0, 0, 0.35);
    border-radius: 2px;
    padding: 0;
    cursor: pointer;
  }

  .sticker:focus-visible {
    outline: 3px solid #1e3a5f;
    outline-offset: 2px;
  }
</style>
