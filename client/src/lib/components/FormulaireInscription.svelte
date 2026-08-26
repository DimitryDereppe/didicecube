<script>
  // Formulaire d'inscription — appelle POST /utilisateurs via le store
  // utilisateur. Contraintes HTML5 (minlength...) : confort de saisie
  // uniquement, la vraie validation reste côté serveur (Joi).
  import { inscrire } from "../stores/utilisateur.js";

  let email = $state("");
  let pseudo = $state("");
  let motDePasse = $state("");
  let erreur = $state("");
  let enCours = $state(false);

  async function soumettre(evenement) {
    evenement.preventDefault();
    erreur = "";
    enCours = true;
    try {
      await inscrire({ email, pseudo, mot_de_passe: motDePasse });
    } catch (e) {
      erreur = e.message;
    } finally {
      enCours = false;
    }
  }
</script>

<form onsubmit={soumettre}>
  <h2>Inscription</h2>

  <p>
    <label for="inscription-email">Email</label>
    <input
      id="inscription-email"
      type="email"
      bind:value={email}
      required
      autocomplete="email"
    />
  </p>

  <p>
    <label for="inscription-pseudo">Pseudo</label>
    <input
      id="inscription-pseudo"
      type="text"
      bind:value={pseudo}
      required
      minlength="3"
      maxlength="30"
      autocomplete="username"
    />
  </p>

  <p>
    <label for="inscription-mot-de-passe">Mot de passe</label>
    <input
      id="inscription-mot-de-passe"
      type="password"
      bind:value={motDePasse}
      required
      minlength="8"
      autocomplete="new-password"
    />
  </p>

  {#if erreur}
    <p class="erreur" role="alert">{erreur}</p>
  {/if}

  <button type="submit" disabled={enCours}>
    {enCours ? "Inscription en cours…" : "Créer mon compte"}
  </button>
</form>
