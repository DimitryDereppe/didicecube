/* Onglet « Accessibilité », présent sur chaque page (socle commun, gabarit Django).
   Usage, dans le <head> de base.html, sans defer (les réglages s'appliquent avant l'affichage, sans clignotement) :
     <link rel="stylesheet" href="{% static 'css/accessibilite.css' %}">
     <script src="{% static 'js/accessibilite.js' %}" data-declaration="{% url 'pages:accessibilite' %}"
       data-cle="nom-du-projet-accessibilite"></script>
   data-declaration : adresse de la déclaration d'accessibilité (par défaut /accessibilite/).
   data-cle : nom du réglage gardé dans le navigateur (un par projet ; par défaut « accessibilite »).
   Sur mobile, l'onglet se pose au-dessus d'une éventuelle barre fixe en bas d'écran marquée data-a11y-barre.
   Couleurs : variables --a11y-* de accessibilite.css, à redéfinir par chaque projet selon sa charte.
   Réglages gardés dans le navigateur du visiteur (localStorage), jamais envoyés : pas de consentement requis.
   Sans JavaScript, l'onglet n'apparaît pas ; le zoom du navigateur reste disponible. */
(function () {
  "use strict";
  var script = document.currentScript || {};
  var donnees = script.dataset || {};
  var CLE = donnees.cle || "accessibilite";
  var LIEN_DECLARATION = donnees.declaration || "/accessibilite/";
  var TAILLES = [100, 115, 130, 150, 175, 200];
  var OPTIONS = [
    ["contraste", "Contraste renforcé"],
    ["gris", "Niveau de gris"],
    ["liens", "Liens soulignés"],
    ["police", "Police plus lisible"],
    ["espacement", "Texte plus espacé"],
    ["sans-animation", "Arrêter les animations"]
  ];
  var racine = document.documentElement;
  var etat = { taille: 100, options: [] };

  try {
    var lu = JSON.parse(localStorage.getItem(CLE) || "null");
    if (lu && TAILLES.indexOf(lu.taille) >= 0 && Array.isArray(lu.options)) etat = lu;
  } catch (e) { /* navigation privée ou stockage bloqué : réglages par défaut */ }

  function appliquer() {
    racine.style.fontSize = etat.taille === 100 ? "" : etat.taille + "%";
    OPTIONS.forEach(function (o) {
      racine.classList.toggle("a11y-" + o[0], etat.options.indexOf(o[0]) >= 0);
    });
  }

  function enregistrer() {
    try {
      if (etat.taille === 100 && !etat.options.length) localStorage.removeItem(CLE);
      else localStorage.setItem(CLE, JSON.stringify(etat));
    } catch (e) { /* sans stockage, le réglage vaut pour la page en cours */ }
  }

  appliquer();

  function construire() {
    var onglet = document.createElement("button");
    onglet.type = "button";
    onglet.className = "a11y-onglet";
    onglet.setAttribute("aria-expanded", "false");
    onglet.setAttribute("aria-controls", "a11y-panneau");
    onglet.innerHTML =
      '<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="26" height="26">' +
      '<circle cx="12" cy="4" r="2" fill="currentColor"/>' +
      '<path d="M4 8.5l8 1.5 8-1.5M12 10v5m0 0l-3.5 6.5M12 15l3.5 6.5" fill="none" stroke="currentColor" ' +
      'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>' +
      '<span class="a11y-libelle">Accessibilité</span>';

    var panneau = document.createElement("section");
    panneau.id = "a11y-panneau";
    panneau.className = "a11y-panneau";
    panneau.setAttribute("aria-labelledby", "a11y-titre");
    panneau.hidden = true;
    var boutons = OPTIONS.map(function (o) {
      return '<li><button type="button" class="a11y-option" data-option="' + o[0] + '" aria-pressed="false">' +
        o[1] + "</button></li>";
    }).join("");
    panneau.innerHTML =
      '<div class="a11y-tete"><h2 id="a11y-titre">Accessibilité</h2>' +
      '<button type="button" class="a11y-fermer">Fermer<span class="a11y-cache"> les réglages d\'accessibilité</span></button></div>' +
      '<p class="a11y-groupe" id="a11y-taille-titre">Taille du texte</p>' +
      '<div class="a11y-taille" role="group" aria-labelledby="a11y-taille-titre">' +
      '<button type="button" data-taille="-1">A−<span class="a11y-cache"> réduire le texte</span></button>' +
      '<output aria-live="polite"></output>' +
      '<button type="button" data-taille="1">A+<span class="a11y-cache"> agrandir le texte</span></button></div>' +
      '<ul class="a11y-options">' + boutons + "</ul>" +
      '<button type="button" class="a11y-reinitialiser">Tout réinitialiser</button>' +
      '<p class="a11y-pied"><a href="' + encodeURI(LIEN_DECLARATION) + '">Déclaration d\'accessibilité</a></p>';

    document.body.appendChild(onglet);
    document.body.appendChild(panneau);

    // Sur mobile, l'onglet et le panneau se posent juste au-dessus d'une barre fixe en bas d'écran, s'il y en a une.
    function placer() {
      var barre = document.querySelector("[data-a11y-barre]");
      var h = barre && getComputedStyle(barre).display !== "none" ? barre.offsetHeight : 0;
      onglet.style.bottom = panneau.style.bottom = h ? h + 8 + "px" : "";
    }
    window.addEventListener("resize", placer);
    window.addEventListener("load", placer);  // après le chargement des polices

    var sortie = panneau.querySelector("output");
    function rafraichir() {
      sortie.textContent = etat.taille + " %";
      panneau.querySelector('[data-taille="-1"]').disabled = etat.taille === TAILLES[0];
      panneau.querySelector('[data-taille="1"]').disabled = etat.taille === TAILLES[TAILLES.length - 1];
      Array.prototype.forEach.call(panneau.querySelectorAll(".a11y-option"), function (b) {
        b.setAttribute("aria-pressed", String(etat.options.indexOf(b.dataset.option) >= 0));
      });
    }

    function ouvrir(oui) {
      panneau.hidden = !oui;
      onglet.setAttribute("aria-expanded", String(oui));
      if (oui) panneau.querySelector("h2").focus();
    }

    panneau.querySelector("h2").tabIndex = -1;
    onglet.addEventListener("click", function () { ouvrir(panneau.hidden); });
    panneau.querySelector(".a11y-fermer").addEventListener("click", function () { ouvrir(false); onglet.focus(); });
    panneau.addEventListener("click", function (ev) {
      var b = ev.target.closest("button");
      if (!b) return;
      if (b.dataset.taille) {
        var i = TAILLES.indexOf(etat.taille) + Number(b.dataset.taille);
        etat.taille = TAILLES[Math.max(0, Math.min(TAILLES.length - 1, i))];
      } else if (b.dataset.option) {
        var k = etat.options.indexOf(b.dataset.option);
        if (k >= 0) etat.options.splice(k, 1); else etat.options.push(b.dataset.option);
      } else if (b.classList.contains("a11y-reinitialiser")) {
        etat = { taille: 100, options: [] };
      } else {
        return;
      }
      appliquer();
      enregistrer();
      rafraichir();
      placer();
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && !panneau.hidden) { ouvrir(false); onglet.focus(); }
    });
    document.addEventListener("click", function (ev) {
      if (!panneau.hidden && !panneau.contains(ev.target) && !onglet.contains(ev.target)) ouvrir(false);
    });
    rafraichir();
    placer();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", construire);
  else construire();
})();
