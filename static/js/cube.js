// Page « Résoudre un cube » : saisie (patron, cube 3D, photo), résolution par le serveur, lecture pas à pas.
// L'état est un tableau de 54 lettres (faces U, D, L, R, F, B ; 9 cases chacune, de gauche à droite et de haut
// en bas). Les mouvements sont des permutations fournies par le serveur (cube/moteur.py) : nouveau[i] = ancien[p[i]].
"use strict";

(function () {
  const D = JSON.parse(document.getElementById("donnees-cube").textContent);
  const FACES = "UDLRFB";
  const NOMS_FACES = { U: "Dessus", D: "Dessous", L: "Gauche", R: "Droite", F: "Avant", B: "Arrière" };
  const CODES = Object.keys(D.couleurs);
  const csrf = document.querySelector("[name=csrfmiddlewaretoken]").value;
  const $ = (id) => document.getElementById(id);

  let etat = (D.progression ? D.progression.etat : D.resolu).split("");
  let couleur = "B";
  let skin = null;
  let sol = null; // { depart, mouvements, etapes, etats, position, etapeDe }
  let progressionId = D.progression ? D.progression.id : null;
  let minuterie = null;

  // Logo au centre de la face avant : il tourne avec la face (F = quart horaire, F' = antihoraire, F2 = demi-tour).
  // L'état en lettres ne garde pas son sens : on compte les quarts de tour à part.
  const CENTRE_F = FACES.indexOf("F") * 9 + 4;
  const QUARTS_F = { F: 1, "F'": -1, F2: 2 };
  const tourneLogo = (q, m) => q + (QUARTS_F[m] || 0);
  let quartsSaisie = 0;
  let angleLogo = 0; // angle affiché, cumulé pour que l'animation prenne le plus court chemin
  const logos = [];

  const applique = (e, m) => D.mouvements[m].map((i) => e[i]);
  const animationsCoupees = () =>
    matchMedia("(prefers-reduced-motion: reduce)").matches ||
    document.documentElement.classList.contains("a11y-sans-animation");

  function message(texte, erreur = false) {
    const p = $("message");
    p.textContent = texte;
    p.classList.toggle("erreur", erreur);
  }

  // --- Construction de l'affichage ------------------------------------------------

  const casesPatron = [];
  const cases3d = [];
  const fleches = {}; // flèche de rotation dessinée sur chaque face 3D

  // Arc de 270° dans le sens des aiguilles d'une montre (vu de face), pointe à gauche ;
  // une seconde pointe en bas pour les demi-tours. Le sens inverse est obtenu par symétrie.
  const SVG_FLECHE = `<svg viewBox="0 0 100 100" aria-hidden="true">
    <g class="fleche3d__trait"><path d="M50 20 A30 30 0 1 1 20 50" fill="none"/>
      <path d="M20 36 L10 55 L30 55 Z"/><path class="fleche3d__demi" d="M36 80 L55 70 L55 90 Z"/></g></svg>`;

  function construit() {
    const palette = $("palette");
    for (const code of CODES) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "pastille";
      b.dataset.code = code;
      b.style.backgroundColor = D.couleurs[code].hex;
      b.setAttribute("aria-label", D.couleurs[code].nom);
      b.addEventListener("click", () => choisitCouleur(code));
      palette.append(b);
    }

    const patron = $("patron");
    const cube = $("cube3d");
    for (const [f, face] of [...FACES].entries()) {
      const grille = document.createElement("div");
      grille.className = `patron__face patron__face--${face}`;
      grille.setAttribute("role", "group");
      grille.setAttribute("aria-label", NOMS_FACES[face]);
      const titre = document.createElement("span");
      titre.className = "patron__nom";
      titre.textContent = `${NOMS_FACES[face]} (${face})`;
      titre.setAttribute("aria-hidden", "true");
      grille.append(titre);

      const face3d = document.createElement("div");
      face3d.className = `face3d face3d--${face}`;

      for (let i = 0; i < 9; i++) {
        const k = f * 9 + i;
        const b = document.createElement("button");
        b.type = "button";
        b.className = "case";
        b.addEventListener("click", () => peint(k));
        grille.append(b);
        casesPatron[k] = b;
        if (k === CENTRE_F) ajouteLogo(b);

        const c = document.createElement("div");
        c.className = "case";
        c.addEventListener("click", () => {
          if (!glisse) peint(k);
        });
        face3d.append(c);
        cases3d[k] = c;
        if (k === CENTRE_F) ajouteLogo(c);
      }
      const fleche = document.createElement("div");
      fleche.className = "fleche3d";
      fleche.hidden = true;
      fleche.innerHTML = `${SVG_FLECHE}<span class="fleche3d__nom"></span>`;
      face3d.append(fleche);
      fleches[face] = fleche;
      patron.append(grille);
      cube.append(face3d);
    }
    choisitCouleur("B");
  }

  function ajouteLogo(caseCentre) {
    const img = document.createElement("img");
    img.src = D.logo;
    img.alt = "";
    img.className = "logo-centre";
    caseCentre.classList.add("case--logo");
    caseCentre.append(img);
    logos.push(img);
  }

  // Tourne le logo vers le sens voulu, par le plus court chemin (un demi-tour se fait dans le sens horaire).
  function orienteLogo(quarts) {
    const cible = (((quarts % 4) + 4) % 4) * 90;
    let ecart = (((cible - angleLogo) % 360) + 360) % 360;
    if (ecart > 180) ecart -= 360;
    angleLogo += ecart;
    for (const img of logos) img.style.transform = `rotate(${angleLogo}deg)`;
  }

  function choisitCouleur(code) {
    couleur = code;
    for (const b of $("palette").children) b.setAttribute("aria-pressed", String(b.dataset.code === code));
  }

  function affiche() {
    const e = sol ? sol.etats[sol.position] : etat;
    orienteLogo(sol ? sol.quarts[sol.position] : quartsSaisie);
    for (let k = 0; k < 54; k++) {
      const code = e[k];
      const nom = D.couleurs[code].nom;
      const i = k % 9;
      for (const el of [casesPatron[k], cases3d[k]]) {
        el.style.backgroundColor = D.couleurs[code].hex;
        el.style.backgroundImage = skin && skin.images[code] ? `url("${skin.images[code]}")` : "";
      }
      casesPatron[k].setAttribute(
        "aria-label",
        `${NOMS_FACES[FACES[Math.floor(k / 9)]]}, ligne ${Math.floor(i / 3) + 1}, colonne ${(i % 3) + 1} : ${nom}`,
      );
      casesPatron[k].disabled = Boolean(sol);
    }
  }

  // Cases qui bougent pendant un mouvement : mises en évidence un instant.
  function surligne(mouvement) {
    const perm = D.mouvements[mouvement];
    const face = FACES.indexOf(mouvement[0]);
    const touchees = [];
    for (let k = 0; k < 54; k++) {
      if (perm[k] !== k || Math.floor(k / 9) === face) touchees.push(k);
    }
    for (const k of touchees) {
      casesPatron[k].classList.add("bouge");
      cases3d[k].classList.add("bouge");
    }
    setTimeout(() => {
      for (const k of touchees) {
        casesPatron[k].classList.remove("bouge");
        cases3d[k].classList.remove("bouge");
      }
    }, 500);
  }

  // --- Saisie ---------------------------------------------------------------------

  function oublieSolution() {
    if (!sol) return;
    arreteLecture();
    sol = null;
    montreProchain(null);
    $("lecteur").hidden = $("pas-3d").hidden = true;
  }

  function peint(k) {
    if (sol) return;
    etat[k] = couleur;
    affiche();
  }

  function remplace(nouvel, quarts = 0) {
    oublieSolution();
    etat = nouvel;
    quartsSaisie = quarts;
    progressionId = null;
    message("");
    affiche();
  }

  $("cube-resolu").addEventListener("click", () => remplace(D.resolu.split("")));
  $("melanger").addEventListener("click", () => {
    const noms = Object.keys(D.mouvements);
    let e = D.resolu.split("");
    let derniere = "";
    let quarts = 0;
    for (let n = 0; n < 25; ) {
      const m = noms[Math.floor(Math.random() * noms.length)];
      if (m[0] === derniere) continue;
      e = applique(e, m);
      quarts = tourneLogo(quarts, m);
      derniere = m[0];
      n++;
    }
    remplace(e, quarts);
  });

  // --- Vue 3D : boutons et glisser ------------------------------------------------

  const VUE_DEPART = [-25, -35];
  let vue = [...VUE_DEPART];
  let glisse = false;

  function oriente() {
    $("cube3d").style.transform = `rotateX(${vue[0]}deg) rotateY(${vue[1]}deg)`;
  }

  for (const b of document.querySelectorAll("[data-vue]")) {
    b.addEventListener("click", () => {
      if (b.dataset.vue === "init") vue = [...VUE_DEPART];
      else {
        const [dx, dy] = b.dataset.vue.split(",").map(Number);
        vue = [vue[0] + dx, vue[1] + dy];
      }
      oriente();
    });
  }

  (function glisser() {
    const scene = $("scene");
    let depart = null;
    scene.addEventListener("pointerdown", (ev) => {
      depart = { x: ev.clientX, y: ev.clientY, vue: [...vue] };
      glisse = false;
    });
    window.addEventListener("pointermove", (ev) => {
      if (!depart) return;
      const dx = ev.clientX - depart.x;
      const dy = ev.clientY - depart.y;
      if (Math.abs(dx) + Math.abs(dy) > 6) glisse = true;
      if (glisse) {
        vue = [depart.vue[0] - dy * 0.5, depart.vue[1] + dx * 0.5];
        oriente();
      }
    });
    window.addEventListener("pointerup", () => {
      depart = null;
      setTimeout(() => (glisse = false), 0);
    });
  })();

  // --- Prochain mouvement sur la vue 3D -------------------------------------------

  // Normales des faces (repère CSS : x à droite, y vers le bas, z vers l'écran).
  const NORMALES = { U: [0, -1, 0], D: [0, 1, 0], L: [-1, 0, 0], R: [1, 0, 0], F: [0, 0, 1], B: [0, 0, -1] };
  // Vues « en coin » (trois faces visibles) proposées quand la face à tourner est cachée.
  const VUES_COIN = [-25, 25].flatMap((a) => [-35, 35, -145, 145].map((b) => [a, b]));

  function faceVisible(face, [ax, ay] = vue) {
    const [x, y, z] = NORMALES[face];
    const a = (ax * Math.PI) / 180;
    const b = (ay * Math.PI) / 180;
    // rotateX(a) rotateY(b) : rotateY s'applique en premier.
    const z1 = -Math.sin(b) * x + Math.cos(b) * z;
    return Math.sin(a) * y + Math.cos(a) * z1 > 0.25;
  }

  // Si la face est cachée, passe à la vue en coin la plus proche qui la montre (plus court chemin).
  function montreFace(face) {
    if (faceVisible(face)) return;
    const proches = VUES_COIN.filter((v) => faceVisible(face, v)).map((v) =>
      v.map((angle, i) => angle + 360 * Math.round((vue[i] - angle) / 360)),
    );
    const ecart = (v) => Math.abs(v[0] - vue[0]) + Math.abs(v[1] - vue[1]);
    vue = proches.reduce((m, v) => (ecart(v) < ecart(m) ? v : m));
    oriente();
  }

  let marquees = [];

  // Flèche sur la face à tourner et cases qui vont bouger encadrées ; null efface tout.
  function montreProchain(mouvement) {
    for (const f of FACES) fleches[f].hidden = true;
    for (const k of marquees) {
      casesPatron[k].classList.remove("a-tourner");
      cases3d[k].classList.remove("a-tourner");
    }
    marquees = [];
    if (!mouvement) return;
    const face = mouvement[0];
    const fleche = fleches[face];
    fleche.classList.toggle("fleche3d--inverse", mouvement[1] === "'");
    fleche.classList.toggle("fleche3d--demi", mouvement[1] === "2");
    fleche.querySelector(".fleche3d__nom").textContent = mouvement;
    fleche.hidden = false;
    const perm = D.mouvements[mouvement];
    const f = FACES.indexOf(face);
    for (let k = 0; k < 54; k++) {
      if (perm[k] !== k || Math.floor(k / 9) === f) marquees.push(k);
    }
    for (const k of marquees) {
      casesPatron[k].classList.add("a-tourner");
      cases3d[k].classList.add("a-tourner");
    }
    montreFace(face);
  }

  // --- Skins ----------------------------------------------------------------------

  if (D.skins.length) {
    $("bloc-skin").hidden = false;
    for (const s of D.skins) {
      const o = document.createElement("option");
      o.value = String(s.id);
      o.textContent = s.nom;
      $("choix-skin").append(o);
    }
    $("choix-skin").addEventListener("change", (ev) => {
      skin = D.skins.find((s) => String(s.id) === ev.target.value) || null;
      affiche();
    });
  }

  // --- Résolution et lecture ------------------------------------------------------

  const SENS = { "": "dans le sens des aiguilles d'une montre", "'": "dans le sens inverse des aiguilles d'une montre", 2: "d'un demi-tour" };

  function decrit(m) {
    const face = NOMS_FACES[m[0]].toLowerCase();
    return `${m} : tourner la face ${face} ${m[1] === "2" ? "" : "d'un quart de tour "}${SENS[m.slice(1)]}.`;
  }

  async function resoudre(etape = 0) {
    arreteLecture();
    message("Calcul de la solution…");
    let reponse;
    try {
      reponse = await fetch(D.urls.solution, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
        body: JSON.stringify({ etat: etat.join("") }),
      });
    } catch {
      message("Le serveur ne répond pas. Réessayez dans un instant.", true);
      return;
    }
    const donnees = await reponse.json().catch(() => ({}));
    if (!reponse.ok) {
      message(donnees.erreur || "La résolution a échoué.", true);
      return;
    }
    const etats = [etat.slice()];
    const quarts = [quartsSaisie];
    for (const m of donnees.mouvements) {
      etats.push(applique(etats[etats.length - 1], m));
      quarts.push(tourneLogo(quarts[quarts.length - 1], m));
    }
    const etapeDe = [];
    donnees.etapes.forEach((e, i) => e.mouvements.forEach(() => etapeDe.push(i)));
    sol = { depart: etat.slice(), mouvements: donnees.mouvements, etapes: donnees.etapes, etats, quarts, position: 0, etapeDe };
    message(
      sol.mouvements.length
        ? `Solution trouvée : ${sol.mouvements.length} mouvements en ${sol.etapes.length} étapes.`
        : "Ce cube est déjà résolu !",
    );
    afficheEtapes();
    $("lecteur").hidden = $("pas-3d").hidden = sol.mouvements.length === 0;
    if (sol.mouvements.length === 0) sol = null;
    else va(Math.min(etape, sol.mouvements.length));
  }

  function afficheEtapes() {
    const liste = $("etapes");
    liste.replaceChildren();
    let n = 0;
    for (const etape of sol.etapes) {
      const li = document.createElement("li");
      const titre = document.createElement("strong");
      titre.textContent = etape.titre;
      const texte = document.createElement("p");
      texte.textContent = etape.explication;
      const mouvements = document.createElement("div");
      mouvements.className = "mouvements";
      for (const m of etape.mouvements) {
        n++;
        const b = document.createElement("button");
        b.type = "button";
        b.className = "mouvement";
        b.textContent = m;
        b.dataset.position = String(n);
        b.setAttribute("aria-label", `Mouvement ${n} : ${m}`);
        const cible = n;
        b.addEventListener("click", () => {
          arreteLecture();
          va(cible);
        });
        mouvements.append(b);
      }
      li.append(titre, texte, mouvements);
      liste.append(li);
    }
  }

  function va(position, anime = false) {
    if (!sol) return;
    position = Math.max(0, Math.min(position, sol.mouvements.length));
    const avance = position === sol.position + 1;
    sol.position = position;
    affiche();
    if (anime && avance && !animationsCoupees()) surligne(sol.mouvements[position - 1]);

    const total = sol.mouvements.length;
    let texte = `Mouvement ${position} sur ${total}`;
    if (position > 0) texte += ` (${sol.etapes[sol.etapeDe[position - 1]].titre}) : ${sol.mouvements[position - 1]}`;
    if (position === total) texte += ". Le cube est résolu !";
    $("position").textContent = texte;
    $("prochain").textContent = position < total ? `Prochain mouvement : ${decrit(sol.mouvements[position])}` : "";
    montreProchain(position < total ? sol.mouvements[position] : null);

    for (const b of $("etapes").querySelectorAll(".mouvement")) {
      const actuel = Number(b.dataset.position) === position;
      b.classList.toggle("fait", Number(b.dataset.position) <= position);
      if (actuel) {
        b.setAttribute("aria-current", "step");
        b.scrollIntoView({ block: "nearest", behavior: animationsCoupees() ? "auto" : "smooth" });
      } else b.removeAttribute("aria-current");
    }
    $("debut").disabled = $("precedent").disabled = $("precedent-3d").disabled = position === 0;
    $("suivant").disabled = $("fin").disabled = $("suivant-3d").disabled = position === total;
    if (position === total) arreteLecture();
  }

  const DELAIS = [1500, 1000, 700, 450, 250];

  function lanceLecture() {
    if (!sol) return;
    if (sol.position === sol.mouvements.length) va(0);
    $("lecture").setAttribute("aria-pressed", "true");
    $("lecture").textContent = "Pause";
    const pas = () => {
      va(sol.position + 1, true);
      if (minuterie !== null) minuterie = setTimeout(pas, DELAIS[$("vitesse").value - 1]);
    };
    minuterie = setTimeout(pas, DELAIS[$("vitesse").value - 1]);
  }

  function arreteLecture() {
    if (minuterie !== null) clearTimeout(minuterie);
    minuterie = null;
    $("lecture").setAttribute("aria-pressed", "false");
    $("lecture").textContent = "Lecture continue";
  }

  $("resoudre").addEventListener("click", () => {
    oublieSolution();
    resoudre();
  });
  $("debut").addEventListener("click", () => { arreteLecture(); va(0); });
  $("precedent").addEventListener("click", () => { arreteLecture(); va(sol.position - 1); });
  $("suivant").addEventListener("click", () => { arreteLecture(); va(sol.position + 1, true); });
  $("precedent-3d").addEventListener("click", () => { arreteLecture(); va(sol.position - 1); });
  $("suivant-3d").addEventListener("click", () => { arreteLecture(); va(sol.position + 1, true); });
  $("fin").addEventListener("click", () => { arreteLecture(); va(sol.mouvements.length); });
  $("modifier").addEventListener("click", () => {
    oublieSolution();
    message("");
    affiche();
  });
  $("lecture").addEventListener("click", () => (minuterie === null ? lanceLecture() : arreteLecture()));

  const boutonEnregistrer = $("enregistrer");
  if (boutonEnregistrer) {
    boutonEnregistrer.addEventListener("click", async () => {
      if (!sol) return;
      const corps = { etat: sol.depart.join(""), etape: sol.position };
      if (progressionId !== null) corps.id = progressionId;
      try {
        const reponse = await fetch(D.urls.enregistrer, {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
          body: JSON.stringify(corps),
        });
        const donnees = await reponse.json();
        if (!reponse.ok) throw new Error(donnees.erreur);
        progressionId = donnees.id;
        message(`Progression enregistrée (mouvement ${sol.position}).`);
      } catch (e) {
        message(e.message || "L'enregistrement a échoué.", true);
      }
    });
  }

  // --- Détection des couleurs par photo -------------------------------------------

  const ORDRE_PHOTO = ["F", "R", "B", "L", "U", "D"];
  const CONSIGNES = {
    F: "Face avant : le dessus du cube en haut de l'image.",
    R: "Face droite (tournez le cube d'un quart de tour vers la gauche) : le dessus en haut de l'image.",
    B: "Face arrière : le dessus en haut de l'image.",
    L: "Face gauche : le dessus en haut de l'image.",
    U: "Dessus : basculez le cube vers vous, la face avant en bas de l'image.",
    D: "Dessous : basculez le cube vers l'arrière, la face avant en haut de l'image.",
  };
  // Couleurs typiques d'un cube photographié, pour reconnaître les centres.
  const REFERENCES = { B: [225, 225, 225], J: [215, 205, 45], R: [180, 30, 40], O: [235, 115, 35], V: [25, 145, 70], L: [25, 70, 170] };
  const echantillons = {};
  let flux = null;

  function lab([r, g, b]) {
    const lin = (c) => ((c /= 255) <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
    const [R, G, B] = [lin(r), lin(g), lin(b)];
    const h = (t) => (t > 0.008856 ? Math.cbrt(t) : 7.787 * t + 16 / 116);
    const x = h((R * 0.4124 + G * 0.3576 + B * 0.1805) / 0.95047);
    const y = h(R * 0.2126 + G * 0.7152 + B * 0.0722);
    const z = h((R * 0.0193 + G * 0.1192 + B * 0.9505) / 1.08883);
    return [116 * y - 16, 500 * (x - y), 200 * (y - z)];
  }
  // La luminosité compte moins que la teinte : un même sticker change de clarté selon l'éclairage.
  const distance = (a, b) => ((a[0] - b[0]) * 0.5) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2;
  const LAB_REF = Object.fromEntries(CODES.map((c) => [c, lab(REFERENCES[c])]));
  const plusProche = (l, refs) => Object.keys(refs).reduce((a, b) => (distance(l, refs[a]) <= distance(l, refs[b]) ? a : b));

  function permutations(liste) {
    if (liste.length <= 1) return [liste];
    return liste.flatMap((x, i) => permutations([...liste.slice(0, i), ...liste.slice(i + 1)]).map((p) => [x, ...p]));
  }

  // Les six faces photographiées : chaque centre reçoit une couleur différente (meilleure combinaison),
  // puis chaque case va vers le centre le plus proche, 9 cases par couleur au plus.
  function classeTout() {
    const labs = {};
    for (const f of FACES) labs[f] = echantillons[f].map(lab);
    let meilleure = null;
    let cout = Infinity;
    for (const p of permutations(CODES)) {
      let c = 0;
      [...FACES].forEach((f, i) => (c += distance(labs[f][4], LAB_REF[p[i]])));
      if (c < cout) [cout, meilleure] = [c, p];
    }
    const refs = {};
    [...FACES].forEach((f, i) => (refs[meilleure[i]] = labs[f][4]));
    const resultat = [];
    const places = Object.fromEntries(CODES.map((c) => [c, 0]));
    const paires = [];
    [...FACES].forEach((f, i) => {
      for (let j = 0; j < 9; j++) {
        const k = i * 9 + j;
        if (j === 4) {
          resultat[k] = meilleure[i];
          places[meilleure[i]]++;
        } else for (const c of CODES) paires.push([distance(labs[f][j], refs[c]), k, c]);
      }
    });
    paires.sort((a, b) => a[0] - b[0]);
    for (const [, k, c] of paires) {
      if (resultat[k] === undefined && places[c] < 9) {
        resultat[k] = c;
        places[c]++;
      }
    }
    return resultat;
  }

  function echantillonne(source, largeur, hauteur) {
    const cote = Math.min(largeur, hauteur);
    const toile = document.createElement("canvas");
    toile.width = toile.height = 150;
    const ctx = toile.getContext("2d", { willReadFrequently: true });
    ctx.drawImage(source, (largeur - cote) / 2, (hauteur - cote) / 2, cote, cote, 0, 0, 150, 150);
    const cases = [];
    for (let i = 0; i < 9; i++) {
      const x = (i % 3) * 50 + 17;
      const y = Math.floor(i / 3) * 50 + 17;
      const px = ctx.getImageData(x, y, 16, 16).data;
      const somme = [0, 0, 0];
      for (let p = 0; p < px.length; p += 4) for (let c = 0; c < 3; c++) somme[c] += px[p + c];
      cases.push(somme.map((s) => s / (px.length / 4)));
    }
    return cases;
  }

  function enregistrePhoto(cases) {
    const face = $("photo-face").value;
    echantillons[face] = cases;
    oublieSolution();
    progressionId = null;
    const nouvelles = FACES.split("").every((f) => echantillons[f]) ? classeTout() : null;
    if (nouvelles) etat = nouvelles;
    else {
      const f = FACES.indexOf(face);
      cases.forEach((rgb, j) => (etat[f * 9 + j] = plusProche(lab(rgb), LAB_REF)));
    }
    affiche();
    const restantes = ORDRE_PHOTO.filter((f) => !echantillons[f]);
    $("photo-etat").textContent = restantes.length
      ? `Face ${NOMS_FACES[face].toLowerCase()} lue. Reste : ${restantes.map((f) => NOMS_FACES[f].toLowerCase()).join(", ")}.`
      : "Les six faces sont lues. Vérifiez les couleurs sur le patron et corrigez-les si besoin.";
    if (restantes.length) {
      $("photo-face").value = restantes[0];
      $("photo-consigne").textContent = CONSIGNES[restantes[0]];
    }
  }

  for (const f of ORDRE_PHOTO) {
    const o = document.createElement("option");
    o.value = f;
    o.textContent = NOMS_FACES[f];
    $("photo-face").append(o);
  }
  $("photo-consigne").textContent = CONSIGNES.F;
  $("photo-face").addEventListener("change", (ev) => ($("photo-consigne").textContent = CONSIGNES[ev.target.value]));

  $("camera").addEventListener("click", async () => {
    if (flux) {
      flux.getTracks().forEach((t) => t.stop());
      flux = null;
      $("viseur").hidden = $("capturer").hidden = true;
      $("camera").textContent = "Activer la caméra";
      return;
    }
    try {
      flux = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
    } catch {
      $("photo-etat").textContent = "Caméra indisponible : choisissez plutôt une photo.";
      return;
    }
    $("video").srcObject = flux;
    await $("video").play();
    $("viseur").hidden = $("capturer").hidden = false;
    $("camera").textContent = "Couper la caméra";
  });

  $("capturer").addEventListener("click", () => {
    const v = $("video");
    if (v.videoWidth) enregistrePhoto(echantillonne(v, v.videoWidth, v.videoHeight));
  });

  $("photo-fichier").addEventListener("change", (ev) => {
    const fichier = ev.target.files[0];
    if (!fichier) return;
    const image = new Image();
    const url = URL.createObjectURL(fichier);
    image.onload = () => {
      enregistrePhoto(echantillonne(image, image.naturalWidth, image.naturalHeight));
      URL.revokeObjectURL(url);
      ev.target.value = "";
    };
    image.onerror = () => ($("photo-etat").textContent = "Image illisible.");
    image.src = url;
  });

  // --- Démarrage ------------------------------------------------------------------

  construit();
  oriente();
  affiche();
  if (D.progression) resoudre(D.progression.etape);
})();
