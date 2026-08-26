<script>
  // Racine de l'app : vérifie la session au chargement, puis affiche soit
  // les formulaires d'authentification, soit le compte connecté.
  import { onMount } from "svelte";
  import { utilisateurConnecte, verifierSession, deconnecter } from "./lib/stores/utilisateur.js";
  import FormulaireConnexion from "./lib/components/FormulaireConnexion.svelte";
  import FormulaireInscription from "./lib/components/FormulaireInscription.svelte";
  import SaisieCube from "./lib/components/SaisieCube.svelte";

  let ongletActif = $state("connexion"); // "connexion" | "inscription"

  onMount(() => {
    verifierSession();
  });
</script>

<header>
  <h1>Didicecube</h1>
  <p>Résolveur de Rubik's Cube</p>
</header>

<main>
  {#if $utilisateurConnecte === undefined}
    <p>Chargement…</p>
  {:else if $utilisateurConnecte}
    <p class="compte">
      Connecté en tant que <strong>{$utilisateurConnecte.pseudo}</strong>
      <button type="button" onclick={deconnecter}>Se déconnecter</button>
    </p>
    <SaisieCube />
  {:else}
    <section aria-label="Authentification">
      <div class="bascule" role="group" aria-label="Choix du formulaire">
        <button
          type="button"
          aria-pressed={ongletActif === "connexion"}
          onclick={() => (ongletActif = "connexion")}
        >
          Connexion
        </button>
        <button
          type="button"
          aria-pressed={ongletActif === "inscription"}
          onclick={() => (ongletActif = "inscription")}
        >
          Inscription
        </button>
      </div>

      {#if ongletActif === "connexion"}
        <FormulaireConnexion />
      {:else}
        <FormulaireInscription />
      {/if}
    </section>
  {/if}
</main>
