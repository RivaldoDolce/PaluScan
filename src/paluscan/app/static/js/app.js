/* PaluScan — interactions : apparitions, planche d'observation, laboratoire d'analyse. */

const REDUIT_MOUVEMENT = matchMedia("(prefers-reduced-motion: reduce)").matches;
const SEUIL_CHARGEMENT = 0.18;

const donnees = JSON.parse(document.getElementById("donnees-metriques").textContent);

const fmt = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 4 });
const fmtPct = new Intl.NumberFormat("fr-FR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const fmtMs = new Intl.NumberFormat("fr-FR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

const $ = (selecteur, racine = document) => racine.querySelector(selecteur);
const $$ = (selecteur, racine = document) => [...racine.querySelectorAll(selecteur)];

function animerCompteur(el, cible, decimales, suffixe = "") {
  const nf = new Intl.NumberFormat("fr-FR", {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  });
  if (REDUIT_MOUVEMENT) {
    el.textContent = nf.format(cible) + suffixe;
    return;
  }
  const debut = performance.now();
  const duree = 900;
  const pas = (maintenant) => {
    const t = Math.min((maintenant - debut) / duree, 1);
    const easing = 1 - Math.pow(1 - t, 3);
    el.textContent = nf.format(cible * easing) + suffixe;
    if (t < 1) requestAnimationFrame(pas);
  };
  requestAnimationFrame(pas);
}

function observerRevelation() {
  const observateur = new IntersectionObserver(
    (entrees) => {
      for (const entree of entrees) {
        if (!entree.isIntersecting) continue;
        entree.target.classList.add("is-visible");
        const valeur = $(".stat-value", entree.target);
        if (valeur && !valeur.dataset.animate) {
          valeur.dataset.animate = "1";
          const brut = valeur.textContent;
          const suffixe = brut.includes("%") ? "\u202f%" : "";
          const texte = brut.replace(/\u202f/g, "").replace(",", ".").replace(/[%\s]/g, "");
          const nombre = parseFloat(texte);
          const decimales = (texte.split(".")[1] || "").length;
          animerCompteur(valeur, nombre, decimales, suffixe);
        }
      }
    },
    { threshold: SEUIL_CHARGEMENT }
  );
  $$(".reveal, .stats-strip .stat").forEach((el) => observateur.observe(el));
}

function installerPlanche() {
  const etiquette = $("#etiquette-planche");
  if (!etiquette) return;
  const defaut = etiquette.textContent;
  const cellules = $$(".planche-cellule");
  for (const cellule of cellules) {
    cellule.addEventListener("mouseenter", () => {
      cellules.forEach((c) => c.classList.remove("is-cible"));
      cellule.classList.add("is-cible");
      etiquette.textContent = `${cellule.dataset.libelle} · lame ${cellule.dataset.lame}`;
    });
  }
  $(".planche-grille").addEventListener("mouseleave", () => {
    etiquette.textContent = defaut;
  });
}

function afficherToast(message) {
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.setAttribute("role", "status");
  toast.textContent = message;
  document.body.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add("is-visible"));
  setTimeout(() => {
    toast.classList.remove("is-visible");
    setTimeout(() => toast.remove(), 300);
  }, 4200);
}

async function posterAnalyse(corps, itineraire) {
  const reponse = await fetch(itineraire, { method: "POST", body: corps });
  const charge = await reponse.json();
  if (!reponse.ok) {
    const erreur = new Error(charge.erreur || "Erreur serveur.");
    erreur.motifs = charge.motifs || [];
    throw erreur;
  }
  return charge;
}

/* ---------- Laboratoire ---------- */

const zoneDepot = $("#zone-depot");
const entreeFichiers = $("#entree-fichiers");
const zoneResultat = $("#zone-resultat");
const corpsLot = $("#corps-lot");
const sectionLot = $("#section-lot");

function afficherAnalyseEnCours(urlApercu) {
  const modele = $("#modele-resultat");
  zoneResultat.replaceChildren(modele.content.cloneNode(true));
  $("[data-champ=apercu]", zoneResultat).src = urlApercu;
  return {
    noeud: zoneResultat,
    conteneur: $("[data-champ=conteneur-visual]", zoneResultat),
  };
}

function afficherRefus(urlApercu, erreur) {
  const modele = $("#modele-refus");
  zoneResultat.replaceChildren(modele.content.cloneNode(true));
  $("[data-champ=refus-apercu]", zoneResultat).src = urlApercu;
  $("[data-champ=refus-message]", zoneResultat).textContent = erreur.message;
  const motifs = $("[data-champ=refus-motifs]", zoneResultat);
  for (const motif of erreur.motifs) {
    const li = document.createElement("li");
    li.textContent = motif;
    motifs.appendChild(li);
  }
}

function installerBasculeCarte(noeud) {
  const bouton = $("[data-champ=bouton-carte]", noeud);
  const carte = $("[data-champ=carte]", noeud);
  bouton.addEventListener("click", () => {
    const actif = bouton.classList.toggle("is-on");
    bouton.setAttribute("aria-pressed", String(actif));
    carte.style.opacity = actif ? "1" : "0";
  });
}

function installerCurseurPrevalence(noeud) {
  const curseur = $("[data-champ=curseur-prevalence]", noeud);
  const libelle = $("[data-champ=valeur-prevalence]", noeud);
  const vpp = $("[data-champ=vpp]", noeud);
  const vpn = $("[data-champ=vpn]", noeud);
  const s = donnees.sensibilite;
  const sp = donnees.specificite;
  const maj = () => {
    const prev = parseFloat(curseur.value) / 100;
    curseur.style.setProperty("--fill", `${(curseur.value / 40) * 100}%`);
    libelle.textContent = `${fmtPct.format(parseFloat(curseur.value))}\u202f%`;
    const pos = (s * prev) / (s * prev + (1 - sp) * (1 - prev));
    const neg = (sp * (1 - prev)) / (sp * (1 - prev) + (1 - s) * prev);
    vpp.textContent = `${fmtPct.format(pos * 100)}\u202f%`;
    vpn.textContent = `${fmtPct.format(neg * 100)}\u202f%`;
  };
  curseur.addEventListener("input", maj);
  maj();
}

async function analyserUnique(fichier) {
  const urlApercu = URL.createObjectURL(fichier);
  const etat = afficherAnalyseEnCours(urlApercu);
  const corps = new FormData();
  corps.append("image", fichier, fichier.name);
  corps.append("occlusion", "1");
  try {
    const r = await posterAnalyse(corps, "/api/analyser");
    remplirResultat(etat, r);
  } catch (erreur) {
    if (erreur.motifs && erreur.motifs.length > 0) {
      afficherRefus(urlApercu, erreur);
    } else {
      afficherVide();
      afficherToast(erreur.message);
    }
  } finally {
    etat.conteneur.classList.remove("is-scan");
  }
}

function remplirResultat(etat, r) {
  const noeud = etat.noeud;
  const infectee = r.infectee;
  const verdict = $("[data-champ=verdict]", noeud);
  verdict.classList.toggle("verdict-infectee", infectee);
  verdict.classList.toggle("verdict-saine", !infectee);
  $("[data-champ=verdict-libelle]", noeud).textContent = infectee
    ? "Cellule parasitée détectée"
    : "Cellule saine";

  const pourcentage = $("[data-champ=pourcentage]", noeud);
  const cercle = $(".jauge-valeur", noeud);
  const circonference = 2 * Math.PI * 76;
  const cible = r.probabilite_infection;
  pourcentage.textContent = fmtPct.format(cible * 100);
  requestAnimationFrame(() => {
    cercle.style.strokeDashoffset = String(circonference * (1 - cible));
  });

  $("[data-champ=p-infectee]", noeud).textContent = `${fmtPct.format(cible * 100)}\u202f%`;
  $("[data-champ=p-sain]", noeud).textContent = `${fmtPct.format(r.probabilite_sain * 100)}\u202f%`;
  $("[data-champ=barre-infectee]", noeud).style.width = `${cible * 100}%`;
  $("[data-champ=barre-sain]", noeud).style.width = `${r.probabilite_sain * 100}%`;

  $("[data-champ=meta-latence]", noeud).textContent = `latence ${fmtMs.format(r.latence_ms)} ms`;
  $("[data-champ=meta-seuil]", noeud).textContent = `seuil de Youden ${fmt.format(r.seuil_youden)}`;

  $("[data-champ=carte]", noeud).src = r.carte;
  installerBasculeCarte(noeud);
  installerCurseurPrevalence(noeud);
}

function afficherVide() {
  const div = document.createElement("div");
  div.className = "result-empty";
  div.innerHTML =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.4 15.4 4.2 4.2"/></svg>' +
    "<p>L'analyse apparaîtra ici</p>" +
    '<p class="result-empty-detail">Importez une image ou choisissez un exemple</p>';
  zoneResultat.replaceChildren(div);
}

async function analyserLot(fichiers) {
  sectionLot.hidden = false;
  corpsLot.replaceChildren();
  const corps = new FormData();
  for (const fichier of fichiers) corps.append("images", fichier, fichier.name);
  const urls = new Map(fichiers.map((f) => [f.name, URL.createObjectURL(f)]));
  try {
    const { resultats } = await posterAnalyse(corps, "/api/analyser-lot");
    resultats.forEach((r, i) => {
      const ligne = $("#modele-ligne-lot").content.cloneNode(true);
      const nom = fichiers[i].name;
      const vignette = $(".cell-mini", ligne);
      vignette.src = urls.get(nom);
      vignette.alt = nom;
      const etiquette = $(".tag", ligne);
      const pInfection = ligne.querySelectorAll("td")[2];
      const latence = ligne.querySelectorAll("td")[3];
      if (r.hors_domaine) {
        etiquette.className = "tag tag-ko";
        etiquette.textContent = "Hors domaine";
        etiquette.title = r.motifs.join(" ");
        pInfection.textContent = "—";
        latence.textContent = "—";
      } else if (r.erreur) {
        etiquette.className = "tag tag-ko";
        etiquette.textContent = "Illisible";
        etiquette.title = r.erreur;
        pInfection.textContent = "—";
        latence.textContent = "—";
      } else {
        etiquette.className = r.infectee ? "tag tag-pos" : "tag tag-neg";
        etiquette.textContent = r.infectee ? "Parasitée" : "Saine";
        pInfection.textContent = `${fmtPct.format(r.probabilite_infection * 100)}\u202f%`;
        latence.textContent = `${fmtMs.format(r.latence_ms)} ms`;
      }
      $("tr", ligne).style.setProperty("--row", String(i));
      corpsLot.appendChild(ligne);
    });
    sectionLot.scrollIntoView({ behavior: REDUIT_MOUVEMENT ? "auto" : "smooth", block: "start" });
  } catch (erreur) {
    if (resultatsVide()) sectionLot.hidden = true;
    afficherToast(erreur.message);
  }
}

function resultatsVide() {
  return corpsLot.children.length === 0;
}

function traiterFichiers(fichiers) {
  const liste = [...fichiers].filter((f) => /^(image\/png|image\/jpeg)$/.test(f.type));
  if (liste.length === 0) {
    afficherToast("Formats acceptés : PNG ou JPEG.");
    return;
  }
  if (liste.length > 12) {
    afficherToast("Maximum 12 images par lot.");
    return;
  }
  if (liste.length === 1) analyserUnique(liste[0]);
  else analyserLot(liste);
}

function installerLaboratoire() {
  if (!zoneDepot) return;
  zoneDepot.addEventListener("click", () => entreeFichiers.click());
  zoneDepot.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      entreeFichiers.click();
    }
  });
  ["dragenter", "dragover"].forEach((nom) =>
    zoneDepot.addEventListener(nom, (e) => {
      e.preventDefault();
      zoneDepot.classList.add("is-drag");
    })
  );
  ["dragleave", "drop"].forEach((nom) =>
    zoneDepot.addEventListener(nom, (e) => {
      e.preventDefault();
      zoneDepot.classList.remove("is-drag");
    })
  );
  zoneDepot.addEventListener("drop", (e) => traiterFichiers(e.dataTransfer.files));
  entreeFichiers.addEventListener("change", () => {
    traiterFichiers(entreeFichiers.files);
    entreeFichiers.value = "";
  });

  $$("[data-exemple]").forEach((vignette) =>
    vignette.addEventListener("click", async () => {
      const reponse = await fetch(vignette.src);
      const contenu = await reponse.blob();
      const fichier = new File([contenu], vignette.src.split("/").pop(), {
        type: contenu.type || "image/png",
      });
      analyserUnique(fichier);
    })
  );
}

observerRevelation();
installerPlanche();
installerLaboratoire();
