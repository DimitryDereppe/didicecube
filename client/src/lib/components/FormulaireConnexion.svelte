<script>
  // Formulaire de connexion — appelle POST /sessions via le store
  // utilisateur. Connexion par pseudo (pas email) : plus simple à retenir.
  import { connecter } from "../stores/utilisateur.js";

  let pseudo = $state("");
  let motDePasse = $state("");
  let erreur = $state("");
  let enCours = $state(false);

  async function soumettre(evenement) {
    evenement.preventDefault();
    erreur = "";
    enCours = true;
    try {
      await connecter({ pseudo, mot_de_passe: motDePasse });
    } catch (e) {
      erreur = e.message;
    } finally {
      enCours = false;
    }
  }
</script>

<form onsubmit={soumettre}>
  <h2>Connexion</h2>

  <p>
    <label for="connexion-pseudo">Pseudo</label>
    <input
      id="connexion-pseudo"
      type="text"
      bind:value={pseudo}
      required
      autocomplete="username"
    />
  </p>

  <p>
    <label for="connexion-mot-de-passe">Mot de passe</label>
    <input
      id="connexion-mot-de-passe"
      type="password"
      bind:value={motDePasse}
      required
      autocomplete="current-password"
    />
  </p>

  {#if erreur}
    <p class="erreur" role="alert">{erreur}</p>
  {/if}

  <button type="submit" disabled={enCours}>
    {enCours ? "Connexion en cours…" : "Se connecter"}
  </button>
</form>
