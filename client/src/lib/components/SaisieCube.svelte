<script>
  // Écran de saisie de l'état de départ du cube : palette de couleurs,
  // cube 3D interactif, sélection de la face active, sauvegarde en
  // progression (API) une fois terminé.
  import {
    FACES,
    NOMS_FACES,
    COULEURS,
    creerCubeResolu,
    versEtatDepart,
    depuisEtatDepart,
  } from "../cube.js";
  import Cube3D from "./Cube3D.svelte";
  import { creerProgression } from "../stores/progressions.js";

  // etatInitial : chaîne de 54 caractères à charger (ex. depuis
  // MesProgressions), ou null pour repartir d'un cube résolu.
  let { etatInitial = null } = $props();

  let cube = $state(creerCubeResolu());
  let faceActive = $state("F");
  let couleurSelectionnee = $state("blanc");
  let message = $state("");
  let enregistrementEnCours = $state(false);

  // Recharge le cube dès que etatInitial change (chargement d'une
  // progression sauvegardée) — les modifications locales ensuite
  // (peindreSticker) ne remontent pas vers etatInitial, pas de boucle.
  $effect(() => {
    cube = etatInitial ? depuisEtatDepart(etatInitial) : creerCubeResolu();
  });

  function peindreSticker(face, index) {
    cube[face][index] = couleurSelectionnee;
  }

  function reinitialiser() {
    cube = creerCubeResolu();
    message = "";
  }

  async function enregistrer() {
    message = "";
    enregistrementEnCours = true;
    try {
      await creerProgression(versEtatDepart(cube));
      message = "État du cube enregistré !";
    } catch (e) {
      message = e.message;
    } finally {
      enregistrementEnCours = false;
    }
  }
</script>

<section aria-labelledby="saisie-titre">
  <h2 id="saisie-titre">Saisir l'état de votre cube</h2>

  <div class="palette" role="group" aria-label="Couleur à appliquer sur les stickers">
    {#each Object.entries(COULEURS) as [nom, info] (nom)}
      <button
        type="button"
        class="swatch"
        style="background-color: {info.hex};"
        aria-pressed={couleurSelectionnee === nom}
        aria-label={info.libelle}
        onclick={() => (couleurSelectionnee = nom)}
      ></button>
    {/each}
  </div>

  <Cube3D {cube} {faceActive} {couleurSelectionnee} onStickerClick={peindreSticker} />

  <div class="faces" role="group" aria-label="Face à afficher/modifier">
    {#each FACES as face (face)}
      <button
        type="button"
        aria-pressed={faceActive === face}
        onclick={() => (faceActive = face)}
      >
        {NOMS_FACES[face]}
      </button>
    {/each}
  </div>

  <div class="actions">
    <button type="button" onclick={reinitialiser}>Réinitialiser</button>
    <button type="button" onclick={enregistrer} disabled={enregistrementEnCours}>
      {enregistrementEnCours ? "Enregistrement…" : "Enregistrer cet état"}
    </button>
  </div>

  {#if message}
    <p role="status">{message}</p>
  {/if}
</section>

<style>
  section {
    text-align: center;
  }

  .palette {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 0.5rem;
  }

  .swatch {
    width: 2.25rem;
    height: 2.25rem;
    border-radius: 50%;
    border: 2px solid #333;
    padding: 0;
    cursor: pointer;
  }

  .swatch[aria-pressed="true"] {
    border-color: var(--couleur-accent, #1e3a5f);
    border-width: 3px;
    box-shadow: 0 0 0 2px white inset;
  }

  .faces,
  .actions {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    flex-wrap: wrap;
    margin: 1rem 0;
  }

  .faces button {
    background: white;
    color: var(--couleur-accent, #1e3a5f);
    border: 1px solid var(--couleur-accent, #1e3a5f);
  }

  .faces button[aria-pressed="true"] {
    background: var(--couleur-accent, #1e3a5f);
    color: white;
  }

  [role="status"] {
    font-weight: 600;
  }
</style>
