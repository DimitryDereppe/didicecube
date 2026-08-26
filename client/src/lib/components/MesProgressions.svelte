<script>
  // Liste des cubes enregistrés : charger un état dans l'éditeur, ou le
  // supprimer. « Charger » recharge juste l'état de départ dans
  // SaisieCube — la vraie reprise de résolution (aller à l'étape atteinte)
  // attend l'algorithme de résolution, pas encore écrit.
  import { onMount } from "svelte";
  import { progressions, chargerProgressions, supprimerProgression } from "../stores/progressions.js";

  let { onCharger } = $props();

  let chargement = $state(true);
  let erreur = $state("");

  onMount(async () => {
    try {
      await chargerProgressions();
    } catch (e) {
      erreur = e.message;
    } finally {
      chargement = false;
    }
  });

  function formaterDate(iso) {
    return new Date(iso).toLocaleString("fr-FR", { dateStyle: "medium", timeStyle: "short" });
  }

  async function supprimer(id) {
    erreur = "";
    try {
      await supprimerProgression(id);
    } catch (e) {
      erreur = e.message;
    }
  }
</script>

<section aria-labelledby="progressions-titre">
  <h2 id="progressions-titre">Mes cubes enregistrés</h2>

  {#if chargement}
    <p>Chargement…</p>
  {:else if erreur}
    <p class="erreur" role="alert">{erreur}</p>
  {/if}

  {#if !chargement}
    {#if $progressions.length === 0}
      <p>Aucun cube enregistré pour l'instant.</p>
    {:else}
      <ul>
        {#each $progressions as progression (progression.id)}
          <li>
            <span>Enregistré le {formaterDate(progression.date_creation)}</span>
            <span class="boutons">
              <button type="button" onclick={() => onCharger(progression.etat_depart)}>
                Charger dans l'éditeur
              </button>
              <button type="button" onclick={() => supprimer(progression.id)}>
                Supprimer
              </button>
            </span>
          </li>
        {/each}
      </ul>
    {/if}
  {/if}
</section>

<style>
  ul {
    list-style: none;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;
    background: white;
    border: 1px solid var(--couleur-bordure, #c4c4c4);
    border-radius: var(--rayon, 0.5rem);
    padding: 0.5rem 0.75rem;
  }

  .boutons {
    display: flex;
    gap: 0.5rem;
  }
</style>
