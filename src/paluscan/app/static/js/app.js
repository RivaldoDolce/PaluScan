/* PaluScan — interactions : révélation, inclinaison 3D, laboratoire d'analyse. */

const REDUIT_MOUVEMENT = matchMedia("(prefers-reduced-motion: reduce)").matches;
const SEUIL_CHARGEMENT = 0.18;

const donnees = JSON.parse(document.getElementById("donnees-metriques").textContent);

const fmt = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 4 });
const fmtPct = new Intl.NumberFormat("fr-FR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const fmtMs = new Intl.NumberFormat("fr-FR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

const $ = (selecteur, racine = document) => racine.querySelector(selecteur);
const $$ = (selecteur, racine = document) => [...racine.querySelectorAll(selecteur)];

function animerCompteur(el, cible, decimales) {
  if (REDUIT_MOUVEMENT) return;
  const debut = performance.now();
  const duree = 1100;
  const nf = new Intl.NumberFormat("fr-FR", {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  });
  const pas = (maintenant) => {
    const t = Math.min((maintenant - debut) / duree, 1);
    const easing = 1 - Math.pow(1 - t, 3);
    el.textContent = nf.format(cible * easing);
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
          const texte = valeur.textContent.replace(/\u202f/g, "").replace(",", ".");
          const nombre = parseFloat(texte);
          const decimales = (texte.split(".")[1] || "").length;
          animerCompteur(valeur, nombre, decimales);
        }
      }
    },
    { threshold: SEUIL_CHARGEMENT }
  );
  $$(".reveal, .stats-strip .stat").forEach((el) => observateur.observe(el));
}

function activerInclinaison() {
  if (REDUIT_MOUVEMENT || !matchMedia("(pointer: fine)").matches) return;
  $$("[data-tilt]").forEach((carte) => {
    let raf = null;
    const bouger = (evenement) => {
      const rect = carte.getBoundingClientRect();
      const x = (evenement.clientX - rect.left) / rect.width;
      const y = (evenement.clientY - rect.top) / rect.height;
      if (raf) return;
      raf = requestAnimationFrame(() => {
        carte.classList.add("is-engaged");
        carte.style.transform = `perspective(900px) rotateX(${(0.5 - y) * 7}deg) rotateY(${(x - 0.5) * 9}deg) translateZ(6px)`;
        carte.style.setProperty("--gx", `${x * 100}%`);
        carte.style.setProperty("--gy", `${y * 100}%`);
        raf = null;
      });
    };
    const sortir = () => {
      if (raf) cancelAnimationFrame(raf);
      raf = null;
      carte.classList.remove("is-engaged");
      carte.style.transform = "";
    };
    carte.addEventListener("pointermove", bouger);
    carte.addEventListener("pointerleave", sortir);
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
    setTimeout(() => toast.remove(), 400);
  }, 4200);
}

async function posterAnalyse(corps, itineraire) {
  const reponse = await fetch(itineraire, { method: "POST", body: corps });
  const charge = await reponse.json();
  if (!reponse.ok) throw new Error(charge.erreur || "Erreur serveur.");
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
  const apercu = $("[data-champ=apercu]", zoneResultat);
  apercu.src = urlApercu;
  return {
    noeud: zoneResultat,
    conteneur: $("[data-champ=conteneur-visual]", zoneResultat),
  };
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
    afficherVide();
    afficherToast(erreur.message);
  } finally {
    etat.conteneur.classList.remove("is-scanning");
  }
}

function remplirResultat(etat, r) {
  const noeud = etat.noeud;
  const infectee = r.infectee;
  const verdict = $("[data-champ=verdict]", noeud);
  verdict.classList.toggle("verdict-infected", infectee);
  verdict.classList.toggle("verdict-healthy", !infectee);
  $("[data-champ=verdict-libelle]", noeud).textContent = infectee
    ? "Cellule parasitée détectée"
    : "Cellule saine";

  const pourcentage = $("[data-champ=pourcentage]", noeud);
  const cercle = $(".gauge-fill", noeud);
  const circonference = 2 * Math.PI * 76;
  const cible = r.probabilite_infection;
  pourcentage.textContent = fmtPct.format(cible * 100);
  requestAnimationFrame(() => {
    cercle.style.strokeDashoffset = String(circonference * (1 - cible));
  });
  animerCompteur(pourcentage, cible * 100, 1);

  const pInfectee = $("[data-champ=p-infectee]", noeud);
  const pSain = $("[data-champ=p-sain]", noeud);
  pInfectee.textContent = fmtPct.format(cible * 100);
  pSain.textContent = fmtPct.format(r.probabilite_sain * 100);
  $("[data-champ=barre-infectee]", noeud).style.width = `${cible * 100}%`;
  $("[data-champ=barre-sain]", noeud).style.width = `${r.probabilite_sain * 100}%`;

  $("[data-champ=meta-latence]", noeud).textContent = `Latence ${fmtMs.format(r.latence_ms)} ms`;
  $("[data-champ=meta-seuil]", noeud).textContent = `Seuil de Youden ${fmt.format(r.seuil_youden)}`;

  const carte = $("[data-champ=carte]", noeud);
  carte.src = r.carte;
  installerBasculeCarte(noeud);
  installerCurseurPrevalence(noeud);
}

function afficherVide() {
  const div = document.createElement("div");
  div.className = "result-empty";
  div.innerHTML =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.4 15.4 4.2 4.2"/></svg>' +
    '<p>L\'analyse apparaîtra ici.</p>' +
    '<p style="font-size:0.85rem;margin-top:0.4rem">Importez une image ou choisissez un exemple.</p>';
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
      $(".cell-mini", ligne).src = urls.get(nom);
      $(".cell-mini", ligne).alt = nom;
      const etiquette = $(".tag", ligne);
      etiquette.className = r.infectee ? "tag tag-pos" : "tag tag-neg";
      etiquette.textContent = r.infectee ? "Parasitée" : "Saine";
      ligne.querySelectorAll("td")[2].textContent = fmtPct.format(r.probabilite_infection * 100);
      ligne.querySelectorAll("td")[3].textContent = `${fmtMs.format(r.latence_ms)} ms`;
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
activerInclinaison();
installerLaboratoire();
