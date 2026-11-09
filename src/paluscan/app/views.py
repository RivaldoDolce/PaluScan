"""Construction des pages HTML : mise en page commune, accueil, démonstration, méthode."""

from __future__ import annotations

import json
from xml.sax.saxutils import escape

from fastcore.xml import NotStr

EXEMPLES = [
    ("para_C182P143NThinF_IMG_20151201_171836_cell_172.png", "Cellule parasitée", "C182P143N"),
    ("para_C66P27N_ThinF_IMG_20150818_163419_cell_195.png", "Cellule parasitée", "C66P27N"),
    ("para_C74P35_ThinF_IMG_20150815_113951_cell_132.png", "Cellule parasitée", "C74P35"),
    ("para_C95P56ThinF_IMG_20150821_172607_cell_95.png", "Cellule parasitée", "C95P56"),
    ("para_C99P60ThinF_IMG_20150918_141129_cell_107.png", "Cellule parasitée", "C99P60"),
    ("para_C99P60ThinF_IMG_20150918_141314_cell_138.png", "Cellule parasitée", "C99P60"),
    ("unin_C100P61ThinF_IMG_20150918_145938_cell_154.png", "Cellule saine", "C100P61"),
    ("unin_C125P86ThinF_IMG_20151004_102053_cell_26.png", "Cellule saine", "C125P86"),
    ("unin_C209ThinF_IMG_20151029_160721_cell_163.png", "Cellule saine", "C209"),
]

ESP = "\u202f"


def _fr(v: float, dec: int = 1) -> str:
    """Format décimal français avec espace insécable avant le signe %."""
    texte = f"{v:.{dec}f}".replace(".", ",")
    return texte.replace(" ", ESP)


def _pct(v: float, dec: int = 1) -> str:
    return f"{_fr(v * 100, dec)}{ESP}%"


def _ent(v: int) -> str:
    """Format entier français : espace fine insécable entre les milliers."""
    return f"{v:,}".replace(",", ESP)


def _icon(trait: str, classe: str = "") -> NotStr:
    return NotStr(
        f'<svg class="{classe}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{trait}</svg>'
    )


ICONE_MARQUE = '<circle cx="12" cy="12" r="8.2"/><path d="M8.4 13.6a4.6 4.6 0 0 0 7.2-1.4"/>'
ICONE_DEPOT = '<path d="M12 15V4m0 0 4 4m-4-4L8 8"/><path d="M4.5 20h15"/>'
ICONE_LOUPE = '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.4 15.4 4.2 4.2"/>'
ICONE_ŒIL = (
    '<path d="M2.2 12S5.8 5.6 12 5.6 21.8 12 21.8 12 18.2 18.4 12 18.4 2.2 12 2.2 12Z"/>'
    '<circle cx="12" cy="12" r="2.7"/>'
)
ICONE_BOUCLIER = '<path d="M12 3l7 2.8V11c0 4.5-3 8.5-7 10-4-1.5-7-5.5-7-10V5.8Z"/><path d="m9 11.6 2.1 2.1L15 9.5"/>'
ICONE_SIGMA = '<path d="M17 5.5H7.4l5.2 6.5-5.2 6.5H17"/>'
ICONE_BASE = '<ellipse cx="12" cy="5.6" rx="7.4" ry="2.7"/><path d="M4.6 5.6v12.8c0 1.5 3.3 2.7 7.4 2.7s7.4-1.2 7.4-2.7V5.6M4.6 12c0 1.5 3.3 2.7 7.4 2.7s7.4-1.2 7.4-2.7"/>'
ICONE_ERLEN = '<path d="M9.2 3h5.6M10.2 3v5.3L4.9 17a2.4 2.4 0 0 0 2.2 3.6h9.8a2.4 2.4 0 0 0 2.2-3.6L13.8 8.3V3"/>'
ICONE_GRAPH = '<path d="M4 4.5v15h16"/><path d="m7 14 3.4-4.2 3 2.6L18.4 7"/>'
ICONE_REJET = '<circle cx="12" cy="12" r="8.2"/><path d="m6.6 6.6 10.8 10.8"/>'


def _nav(active: str) -> str:
    liens = {"accueil": "Accueil", "demo": "Démonstration", "methode": "Méthode"}
    items = "".join(
        f'<a href="/{ancre if ancre != "accueil" else ""}" class="{"is-active" if ancre == active else ""}">{libelle}</a>'
        for ancre, libelle in liens.items()
    )
    return f'<div class="container nav-inner"><a href="/" class="brand"><span class="brand-mark">{_icon(ICONE_MARQUE)}</span><span class="brand-nom">PaluScan<small>Vision par ordinateur · Hématologie</small></span></a><nav class="nav-links" aria-label="Navigation principale">{items}</nav><a href="/demo" class="nav-cta">Analyser une cellule</a></div>'


def _pied() -> str:
    return (
        '<footer class="footer"><div class="container footer-inner">'
        "<p>PaluScan — projet d'étude de vision par ordinateur, sans visée diagnostique.</p>"
        '<div class="footer-links"><a href="/demo">Démonstration</a><a href="/methode">Méthode</a>'
        '<a href="https://github.com/RivaldoDolce/PaluScan" target="_blank" rel="noopener">Code source</a></div>'
        "<p>Données : NIH / LSHTM · Licence CC BY 4.0</p>"
        "</div></footer>"
    )


def _planche_cellules() -> str:
    """Planche d'observation du héros : neuf cellules réelles du corpus, étiquettes au survol."""
    vignettes = "".join(
        f'<button type="button" class="planche-cellule{" is-cible" if i == 0 else ""}" '
        f'data-libelle="{libelle}" data-lame="{lame}" aria-label="{libelle}, lame {lame}">'
        f'<img src="/static/img/exemples/{nom}" alt="" loading="eager" width="64" height="64">'
        f"</button>"
        for i, (nom, libelle, lame) in enumerate(EXEMPLES)
    )
    return (
        '<figure class="planche" aria-label="Planche de neuf cellules du corpus NIH">'
        '<figcaption class="planche-tete"><span>Planche d\u2019observation</span>'
        "<span>Corpus NIH · 64×64 px</span></figcaption>"
        f'<div class="planche-grille">{vignettes}</div>'
        '<figcaption class="planche-pied"><span class="planche-etiquette" id="etiquette-planche">'
        "Survolez une cellule pour lire son étiquette</span></figcaption>"
        "</figure>"
    )


def _strip_chiffres(m: dict) -> str:
    valeurs = [
        (_fr(m["auc"]["valeur"], 4), "AUC ROC, jeu de test"),
        (_pct(m["sensibilite"]["valeur"]), "Sensibilité"),
        (_pct(m["specificite"]["valeur"]), "Spécificité"),
        (_ent(m["n_test"]), "Cellules de test"),
    ]
    corps = "".join(
        f'<div class="stat rise" style="--rise-delay:{i * 60}ms"><div class="stat-value">{v}</div>'
        f'<div class="stat-label">{libelle}</div></div>'
        for i, (v, libelle) in enumerate(valeurs)
    )
    return f'<div class="container section"><div class="stats-strip">{corps}</div></div>'


def _page_base(titre: str, active: str, corps: str, metriques: dict) -> NotStr:
    description = (
        "PaluScan : détection du paludisme sur frottis sanguins par un réseau convolutif léger, "
        "avec explicabilité par occlusion, garde-fou d'entrée et statistique inférentielle."
    )
    head = (
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{escape(titre)}</title>"
        f'<meta name="description" content="{description}">'
        '<link rel="icon" href="/static/img/favicon.svg" type="image/svg+xml">'
        '<link rel="preload" href="/static/fonts/plex-sans-var.woff2" as="font" type="font/woff2" crossorigin>'
        '<link rel="preload" href="/static/fonts/plex-mono-400.woff2" as="font" type="font/woff2" crossorigin>'
        '<link rel="stylesheet" href="/static/css/style.css">'
        f'<script type="application/json" id="donnees-metriques">{escape(json.dumps({"seuil": metriques.get("seuil_youden", 0.5), "sensibilite": metriques.get("sensibilite", {}).get("valeur", 0.9677), "specificite": metriques.get("specificite", {}).get("valeur", 0.9541)}))}</script>'
        '<script type="module" src="/static/js/app.js"></script>'
    )
    html = f'<!DOCTYPE html><html lang="fr"><head>{head}</head><body><header class="nav">{_nav(active)}</header><main>{corps}</main>{_pied()}</body></html>'
    return NotStr(html)


def page_accueil(m: dict) -> NotStr:
    """Page d'accueil : héros, chiffres clés, protocole, capacités et appel à l'action."""
    hero = f"""
<section class="hero"><div class="container hero-grid">
  <div>
    <p class="kicker rise">Détection du paludisme</p>
    <h1 class="rise" style="--rise-delay:60ms">Lire un frottis sanguin, cellule par cellule</h1>
    <p class="hero-lede rise" style="--rise-delay:120ms">PaluScan estime la probabilité d'infection par
    <em>Plasmodium</em> sur une image microscopique, accompagne chaque décision d'une carte d'occlusion
    et refuse les images qui ne sont pas des frottis colorés au Giemsa. Réseau convolutif de 62{ESP}000
    paramètres, inférence ONNXRuntime sur simple processeur.</p>
    <div class="hero-actions rise" style="--rise-delay:180ms">
      <a href="/demo" class="btn btn-primaire">{_icon(ICONE_LOUPE)} Ouvrir le laboratoire</a>
      <a href="/methode" class="btn btn-neutre">Comprendre la méthode</a>
    </div>
    <p class="hero-meta rise" style="--rise-delay:240ms">AUC {_fr(m["auc"]["valeur"], 4)} · IC95 {_fr(m["auc"]["ic95"][0], 3)}–{_fr(m["auc"]["ic95"][1], 3)} · {_ent(m["n_test"])} cellules de test · inférence &lt; 10 ms</p>
  </div>
  {_planche_cellules()}
</div></section>"""
    pipeline = f"""
<section class="section"><div class="container">
  <div class="section-head reveal">
    <p class="kicker">Protocole</p>
    <h2 class="section-title">Trois étapes, une seule exigence&nbsp;: la rigueur</h2>
    <p class="section-sub">Chaque décision méthodologique — découpage des données, architecture,
    statistique de test — a été prise pour produire des résultats honnêtes et reproductibles.</p>
  </div>
  <div class="grid-3">
    <article class="card reveal" style="--reveal-delay:0ms">
      <div class="card-tete"><span class="step-num">01</span>{_icon(ICONE_BASE, "card-icone")}</div>
      <h3>Données maîtrisées</h3><p>27{ESP}558 cellules issues du jeu public NIH / LSHTM, auditées puis
      réparties <strong>par lame</strong> (212 lames de test) pour éliminer toute fuite d'information entre
      entraînement et évaluation.</p>
    </article>
    <article class="card reveal" style="--reveal-delay:60ms">
      <div class="card-tete"><span class="step-num">02</span>{_icon(ICONE_ERLEN, "card-icone")}</div>
      <h3>Apprentissage encadré</h3><p>MalariaNet, un réseau convolutif de 62{ESP}000 paramètres, entraîné
      avec augmentation géométrique et photométrique, arrêt anticipé et suivi d'AUC par validation.</p>
    </article>
    <article class="card reveal" style="--reveal-delay:120ms">
      <div class="card-tete"><span class="step-num">03</span>{_icon(ICONE_GRAPH, "card-icone")}</div>
      <h3>Évaluation honnête</h3><p>Intervalles de Wilson, bootstrap à 10{ESP}000 tirages, seuil de Youden,
      calibration et test de McNemar face à la baseline&nbsp;: les chiffres annoncés encadrent la performance réelle.</p>
    </article>
  </div>
</div></section>"""
    capacites = f"""
<section class="section"><div class="container">
  <div class="section-head reveal">
    <p class="kicker">Capacités</p>
    <h2 class="section-title">Un modèle qui montre son travail</h2>
  </div>
  <div class="grid-2">
    <article class="card reveal">
      <div class="card-tete">{_icon(ICONE_BOUCLIER, "card-icone")}<h3>Découpage par lame, sans fuite</h3></div>
      <p>Les cellules d'une même lame se ressemblent presque parfaitement. Le découpage garantit qu'aucune lame
      n'apparaît à la fois dans l'entraînement et le test — un biais classique qui gonfle artificiellement l'AUC.</p>
    </article>
    <article class="card reveal" style="--reveal-delay:60ms">
      <div class="card-tete">{_icon(ICONE_ŒIL, "card-icone")}<h3>Cartes d'occlusion</h3></div>
      <p>En masquant des fenêtres de l'image et en mesurant la chute du logit, l'application superpose une
      carte de chaleur&nbsp;: le parasite détecté devient visible, vérifiable, contestable.</p>
    </article>
    <article class="card reveal">
      <div class="card-tete">{_icon(ICONE_REJET, "card-icone")}<h3>Garde-fou d'entrée</h3></div>
      <p>Avant toute prédiction, un contrôle statistique vérifie la palette Giemsa, le grain de coloration
      et la structure cellulaire. Photos, captures d'écran et documents sont refusés avec leurs motifs.</p>
    </article>
    <article class="card reveal" style="--reveal-delay:60ms">
      <div class="card-tete">{_icon(ICONE_SIGMA, "card-icone")}<h3>Statistique écrite à la main</h3></div>
      <p>Wilson, bootstrap et test de McNemar sont implémentés sans dépendance lourde&nbsp;:
      le code d'évaluation tient dans un fichier, lisible ligne par ligne.</p>
    </article>
  </div>
</div></section>"""
    cta = """
<section class="section"><div class="container">
  <div class="bande reveal">
    <h2>Analysez une cellule du jeu de test</h2>
    <p>Neuf images du corpus sont fournies, ou importez vos propres frottis. Les images hors domaine
    sont refusées avant toute prédiction, avec les motifs du refus.</p>
    <div class="hero-actions">
      <a href="/demo" class="btn btn-primaire">Ouvrir le laboratoire</a>
      <a href="/methode" class="btn btn-neutre">Lire les résultats</a>
    </div>
  </div>
</div></section>"""
    corps = hero + _strip_chiffres(m) + pipeline + capacites + cta
    return _page_base("PaluScan — Détection du paludisme sur frottis sanguins", "accueil", corps, m)


def page_demo(m: dict) -> NotStr:
    """Page de démonstration : zone de dépôt, exemples, gabarits de résultat et de refus."""
    vignettes = "".join(
        f'<img class="thumb" src="/static/img/exemples/{nom}" alt="{alt}, lame {lame}" loading="lazy" '
        f'data-exemple width="52" height="52">'
        for nom, alt, lame in EXEMPLES
    )
    zone = f"""
<section class="section"><div class="container">
  <div class="section-head reveal">
    <p class="kicker">Laboratoire interactif</p>
    <h2 class="section-title">Analysez une cellule en un clic</h2>
    <p class="section-sub">Déposez une ou plusieurs images (PNG, JPEG). Chaque image passe d'abord le
    contrôle de domaine&nbsp;: photos, captures d'écran et documents sont refusés avec leurs motifs,
    sans diagnostic. Les frottis reçoivent une décision au seuil de Youden, une probabilité
    d'infection et une carte d'occlusion.</p>
  </div>
  <div class="analyzer">
    <div class="card reveal">
      <div class="dropzone" id="zone-depot" role="button" tabindex="0" aria-label="Déposer des images à analyser">
        <input type="file" id="entree-fichiers" accept="image/png,image/jpeg" multiple hidden>
        <div class="dropzone-icon">{_icon(ICONE_DEPOT)}</div>
        <strong>Déposez vos images</strong>
        <span>PNG ou JPEG · 8{ESP}Mo max · 12 fichiers au plus, ou cliquez pour parcourir</span>
      </div>
      <div class="examples">
        <p class="examples-titre">Exemples du jeu de test</p>
        <div class="examples-row">{vignettes}</div>
      </div>
    </div>
    <div class="card reveal" style="--reveal-delay:60ms">
      <div id="zone-resultat" class="result" aria-live="polite">
        <div class="result-empty">
          {_icon(ICONE_LOUPE)}
          <p>L'analyse apparaîtra ici</p>
          <p class="result-empty-detail">Importez une image ou choisissez un exemple</p>
        </div>
      </div>
    </div>
  </div>
  <section id="section-lot" class="section-lot" hidden>
    <h2 class="section-title section-title-moyen">Analyse en lot</h2>
    <div class="table-wrap">
      <table class="batch">
        <thead><tr><th>Image</th><th>Décision</th><th>P(infection)</th><th>Latence</th></tr></thead>
        <tbody id="corps-lot"></tbody>
      </table>
    </div>
  </section>
</div></section>"""
    modele_resultat = f"""
<template id="modele-resultat">
  <div class="verdict verdict-saine" data-champ="verdict"><span class="verdict-dot"></span><span data-champ="verdict-libelle">Saine</span></div>
  <div class="jauge-wrap">
    <div class="jauge">
      <svg viewBox="0 0 172 172" width="172" height="172" role="img" aria-label="Probabilité d'infection">
        <circle class="jauge-piste" cx="86" cy="86" r="76"/>
        <circle class="jauge-valeur" cx="86" cy="86" r="76" stroke-dasharray="477.5" stroke-dashoffset="477.5"/>
      </svg>
      <div class="jauge-centre"><div class="jauge-nombre" data-champ="pourcentage">0{ESP}%</div>
      <div class="jauge-legende">probabilité d'infection</div></div>
    </div>
    <div class="prob-bars">
      <div class="prob-row"><div class="prob-head"><span>Parasitée</span><span data-champ="p-infectee">—</span></div>
        <div class="prob-track"><div class="prob-fill prob-infectee" data-champ="barre-infectee"></div></div></div>
      <div class="prob-row"><div class="prob-head"><span>Saine</span><span data-champ="p-sain">—</span></div>
        <div class="prob-track"><div class="prob-fill prob-saine" data-champ="barre-sain"></div></div></div>
      <div class="result-meta">
        <span data-champ="meta-latence">latence —</span>
        <span data-champ="meta-seuil">seuil de Youden —</span>
        <span>ONNXRuntime · CPU</span>
      </div>
    </div>
  </div>
  <div class="jauge-wrap">
    <div class="apercu is-scan" data-champ="conteneur-visual">
      <img data-champ="apercu" src="" alt="Cellule analysée" width="148" height="148">
      <img data-champ="carte" src="" alt="Carte d'occlusion superposée" width="148" height="148"
           style="position:absolute;inset:0;opacity:1;transition:opacity .2s var(--ease)">
      <span class="apercu-progres"></span>
    </div>
    <div>
      <button type="button" class="toggle is-on" data-champ="bouton-carte" aria-pressed="true">
        <span class="knob"></span> Carte d'occlusion
      </button>
      <p class="note">La carte signale les régions dont le masquage réduit le plus
      la confiance du modèle — le parasite détecté apparaît en rouge</p>
    </div>
  </div>
  <div class="slider-block">
    <div class="slider-head"><span>Prévalence locale du paludisme</span><span class="slider-value mono" data-champ="valeur-prevalence">1,0{ESP}%</span></div>
    <input type="range" min="0.1" max="40" step="0.1" value="1" data-champ="curseur-prevalence" aria-label="Prévalence locale">
    <div class="ppv-grid">
      <div class="ppv-cell pos"><div class="ppv-label">VPP · prédire infecté</div><div class="ppv-value mono" data-champ="vpp">—</div></div>
      <div class="ppv-cell neg"><div class="ppv-label">VPN · prédire sain</div><div class="ppv-value mono" data-champ="vpn">—</div></div>
    </div>
    <p class="note">Valeurs prédictives recalculées par la règle de Bayes à partir de la sensibilité
    ({_pct(m.get("sensibilite", {}).get("valeur", 0.9677))}) et de la spécificité
    ({_pct(m.get("specificite", {}).get("valeur", 0.9541))}) mesurées sur le jeu de test</p>
  </div>
</template>"""
    modele_refus = """
<template id="modele-refus">
  <div class="verdict verdict-refus"><span class="verdict-dot"></span><span>Image hors domaine</span></div>
  <div class="refus-corps">
    <img class="refus-apercu" data-champ="refus-apercu" src="" alt="Image refusée" width="108" height="108">
    <div class="refus-raison">
      <p class="refus-message" data-champ="refus-message"></p>
      <ul class="refus-motifs" data-champ="refus-motifs"></ul>
    </div>
  </div>
  <p class="note">Aucun diagnostic n'est produit&nbsp;: PaluScan n'analyse que des images de cellules
  colorées au Giemsa. Contrôle détaillé sur la page Méthode</p>
</template>"""
    modele_ligne = """
<template id="modele-ligne-lot">
  <tr><td><img class="cell-mini" src="" alt="" width="44" height="44"></td>
  <td><span class="tag tag-muet">—</span></td><td>—</td><td>—</td></tr>
</template>"""
    corps = zone + modele_resultat + modele_refus + modele_ligne
    return _page_base("Démonstration — PaluScan", "demo", corps, m)


# ---------- Graphiques SVG (chaînes brutes : attributs viewBox camelCase) ----------

LARG, HAUT, X0, Y0 = 340, 250, 42, 12
LARGEUR_PLOT, HAUTEUR_PLOT = LARG - X0 - 14, HAUT - Y0 - 30


def _cadre(unites: list[tuple[float, str]] | None = None) -> str:
    """Axe et grille commune aux courbes en coordonnées 0–1."""
    traits = ""
    for u in [0, 0.5, 1]:
        x = X0 + u * LARGEUR_PLOT
        y = Y0 + (1 - u) * HAUTEUR_PLOT
        libelle = escape(_fr(u, 1))
        traits += (
            f'<line x1="{x:.1f}" y1="{Y0}" x2="{x:.1f}" y2="{Y0 + HAUTEUR_PLOT}" stroke="rgba(236,234,242,0.07)" stroke-width="1"/>'
            f'<line x1="{X0}" y1="{y:.1f}" x2="{X0 + LARGEUR_PLOT}" y2="{y:.1f}" stroke="rgba(236,234,242,0.07)" stroke-width="1"/>'
            f'<text x="{x:.1f}" y="{Y0 + HAUTEUR_PLOT + 16}" font-size="10" fill="#837e90" text-anchor="middle">{libelle}</text>'
            f'<text x="{X0 - 7}" y="{y + 3:.1f}" font-size="10" fill="#837e90" text-anchor="end">{libelle}</text>'
        )
    return traits


def _courbe(xs: list[float], ys: list[float], classe: str, delai: int = 0) -> str:
    points = " ".join(
        f"{X0 + x * LARGEUR_PLOT:.1f},{Y0 + (1 - y) * HAUTEUR_PLOT:.1f}"
        for x, y in zip(xs, ys, strict=False)
    )
    return f'<polyline class="{classe}" points="{points}" style="animation-delay:{delai}ms"/>'


def _svg(titre: str, sous_texte: str, contenu: str, etiquette: str = "") -> str:
    return f"""
<div class="card chart-card">
  <div class="chart-title"><h3>{titre}</h3><span class="mono">{sous_texte}</span></div>
  <svg class="chart-svg" viewBox="0 0 {LARG} {HAUT}" role="img" aria-label="{escape(etiquette or titre)}">
    {_cadre()}{contenu}
  </svg>
</div>"""


def _carte_roc(m: dict) -> str:
    roc = m["roc"]
    courbe = _courbe(roc["fpr"], roc["tpr"], "chart-line")
    diagonale = _courbe([0, 1], [0, 1], "chart-line chart-neutre")
    return _svg(
        "Courbe ROC",
        f"AUC {_fr(m['auc']['valeur'], 4)} · IC95 {_fr(m['auc']['ic95'][0], 3)}–{_fr(m['auc']['ic95'][1], 3)}",
        courbe + diagonale,
    )


def _carte_pr(m: dict) -> str:
    pr = m["pr"]
    courbe = _courbe(pr["rappel"], pr["precision"], "chart-line", delai=120)
    return _svg("Précision–rappel", f"Précision moyenne {_fr(m['precision_moyenne'], 4)}", courbe)


def _carte_calibration(m: dict) -> str:
    cal = m["calibration"]
    diagonale = _courbe([0, 1], [0, 1], "chart-line chart-neutre")
    points = "".join(
        f'<circle cx="{X0 + c * LARGEUR_PLOT:.1f}" cy="{Y0 + (1 - o) * HAUTEUR_PLOT:.1f}" r="3.2" '
        f'fill="var(--carmin)" stroke="var(--fond)" stroke-width="1.4"/>'
        for c, o in zip(cal["confiance"], cal["observe"], strict=False)
    )
    segment = _courbe(cal["confiance"], cal["observe"], "chart-line", delai=200)
    return _svg("Calibration", "Observé contre prédit (10 classes)", diagonale + segment + points)


def _carte_perte(m: dict) -> str:
    e = m["entrainement"]
    n = len(e["epoques"])
    x_train = [i / (n - 1) for i in range(n)]
    y_max = max(max(e["perte_train"]), max(e["perte_val"])) * 1.08
    train = _courbe(x_train, [v / y_max for v in e["perte_train"]], "chart-line")
    val = _courbe(
        x_train, [v / y_max for v in e["perte_val"]], "chart-line chart-neutre", delai=160
    )
    legende = (
        '<span class="legende-ligne"><i class="fil fil-carmin"></i>entraînement</span>'
        '<span class="legende-ligne"><i class="fil fil-neutre"></i>validation</span>'
    )
    return f"""
<div class="card chart-card">
  <div class="chart-title"><h3>Perte par époque</h3><span class="legende">{legende}</span></div>
  <svg class="chart-svg" viewBox="0 0 {LARG} {HAUT}" role="img" aria-label="Évolution de la perte d'entraînement et de validation">
    {_cadre()}{train}{val}
  </svg>
</div>"""


def _carte_confusion(m: dict) -> str:
    c = m["matrice_confusion"]

    def cellule(nombre: int, sous: str, classe: str) -> str:
        return (
            f'<div class="conf-cell {classe}"><span class="mono conf-nombre">{nombre}</span>'
            f'<span class="conf-sous">{sous}</span></div>'
        )

    entete = '<div></div><div class="conf-head">Prédit · infecté</div><div class="conf-head">Prédit · sain</div>'
    return f"""
<div class="card chart-card">
  <div class="chart-title"><h3>Matrice de confusion</h3><span class="mono">Seuil de Youden {_fr(m["seuil_youden"], 4)}</span></div>
  <div class="conf-grid">
    {entete}
    <div class="conf-side">Réel · infecté</div>{cellule(c["vp"], "vrais positifs", "conf-tp")}{cellule(c["fn"], "faux négatifs", "conf-fn")}
    <div class="conf-side">Réel · sain</div>{cellule(c["fp"], "faux positifs", "conf-fp")}{cellule(c["vn"], "vrais négatifs", "conf-tn")}
  </div>
</div>"""


def _carte_intervalles(m: dict) -> str:
    lignes = ""
    for i, (nom, cle) in enumerate(
        [
            ("Exactitude", "exactitude"),
            ("Sensibilité", "sensibilite"),
            ("Spécificité", "specificite"),
        ]
    ):
        v = m[cle]
        gauche, droite = v["ic95"]
        band = f"left:{gauche * 100:.1f}%;width:{(droite - gauche) * 100:.1f}%;animation-delay:{i * 90}ms"
        dot = f"left:{v['valeur'] * 100:.1f}%"
        lignes += (
            f'<div class="ci-row"><span>{nom}</span>'
            f'<span class="ci-track"><span class="ci-band" style="{band}"></span>'
            f'<span class="ci-dot" style="{dot}"></span></span>'
            f'<span class="mono">{_pct(gauche, 1)} – {_pct(droite, 1)}</span></div>'
        )
    return f"""
<div class="card chart-card">
  <div class="chart-title"><h3>Intervalles de confiance à 95{ESP}%</h3><span class="mono">{_ent(m["n_test"])} cellules · {m["n_test_slides"]} lames</span></div>
  {lignes}
</div>"""


def _carte_baseline(m: dict) -> str:
    b = m["baseline"]
    mc = m["mcnemar"]

    def barre(valeur: float, classe: str, delai: int) -> str:
        return (
            f'<div class="prob-track"><div class="prob-fill {classe}" '
            f'style="width:{valeur * 100:.1f}%;transition-delay:{delai}ms"></div></div>'
        )

    return f"""
<div class="card chart-card">
  <div class="chart-title"><h3>Contre la baseline</h3><span class="mono">Test de McNemar</span></div>
  <div class="baseline-corps">
    <div class="prob-head"><span>MalariaNet (CNN)</span><span class="mono">AUC {_fr(m["auc"]["valeur"], 4)}</span></div>
    {barre(m["auc"]["valeur"], "prob-carmin", 100)}
    <div class="prob-head prob-head-ecart"><span>{escape(b["nom"])}</span><span class="mono">AUC {_fr(b["auc"], 4)}</span></div>
    {barre(b["auc"], "prob-neutre", 220)}
  </div>
  <p class="note">Sur les {_ent(mc["n_discordantes"])} cellules tranchées différemment, la baseline se trompe seule
  {_ent(mc["b_base_seulement"])} fois contre {_ent(mc["c_cnn_seulement"])} pour le CNN (p &lt; 0,001)&nbsp;: l'écart est
  significatif, pas un artefact d'échantillonnage</p>
</div>"""


def _carte_garde_fou() -> str:
    barre_c = (
        '<div class="prob-track"><div class="prob-fill prob-saine" style="width:98.8%"></div></div>'
    )
    barre_r = '<div class="prob-track"><div class="prob-fill prob-carmin" style="width:97.4%"></div></div>'
    return f"""
<div class="card chart-card">
  <div class="chart-title"><h3>Garde-fou d'entrée</h3><span class="mono">Banc d'essai de calibration</span></div>
  <div class="baseline-corps">
    <div class="prob-head"><span>Cellules du corpus acceptées</span><span class="mono">316 / 320 · {_pct(316 / 320)}</span></div>
    {barre_c}
    <div class="prob-head prob-head-ecart"><span>Contre-exemples refusés</span><span class="mono">76 / 78 · {_pct(76 / 78)}</span></div>
    {barre_r}
  </div>
  <p class="note">Contrôle statistique avant toute prédiction&nbsp;: dôme de couleur Giemsa (distance de
  Mahalanobis ajustée sur 160 cellules), saturation, grain de coloration, bords nets, matière dense et
  part de fond pâle. Deux contre-exemples adverses — une photo sombre délibérément recolorée — passent
  encore le contrôle&nbsp;: la limite est documentée dans la discussion</p>
</div>"""


def page_methode(m: dict) -> NotStr:
    """Page méthode : tableau de bord graphique, garde-fou, prose rédigée et chronologie."""
    dashboard = f"""
<section class="section" style="padding-top:0"><div class="container">
  <div class="section-head reveal">
    <p class="kicker">Résultats</p>
    <h2 class="section-title">Ce que dit le jeu de test</h2>
    <p class="section-sub">Aucune métrique isolée&nbsp;: chaque chiffre est accompagné de son intervalle
    de confiance, de la courbe qui le justifie et du test statistique qui le confronte à la baseline.</p>
  </div>
  <div class="grid-2">
    {_carte_roc(m)}{_carte_calibration(m)}
    {_carte_perte(m)}{_carte_confusion(m)}
    {_carte_intervalles(m)}{_carte_baseline(m)}
    {_carte_garde_fou()}{_carte_pr(m)}
  </div>
</div></section>"""
    prose = f"""
<section class="section"><div class="container prose">
  <p class="kicker reveal">Méthode</p>
  <h2 class="reveal">Le jeu de données</h2>
  <p class="reveal">Le corpus provient du jeu public NIH / LSHTM&nbsp;: 27&nbsp;558 images de cellules
  individuelles, découpées à 64×64 pixels depuis des frottis sanguins minces colorés au Giemsa,
  étiquetées par microscopistes — 13&nbsp;779 parasitées, 13&nbsp;779 saines. Le jeu est notoirement
  déséquilibré dans les faits&nbsp;: quelques « saines » sont des globules blancs, artefact de recadrage
  documenté par les réutilisations ultérieures du corpus. Il est utilisé ici tel quel, et cette limite
  est assumée dans la discussion.</p>
  <h2 class="reveal">La fuite statistique, ennemie n°&nbsp;1</h2>
  <p class="reveal">Les cellules d'une même lame proviennent du même patient, de la même goutte de sang,
  du même réglage optique&nbsp;: elles sont quasi jumelles. Un découpage aléatoire image par image place
  donc des jumelles du jeu d'entraînement dans le jeu de test et gonfle artificiellement toutes les
  métriques. PaluScan découpe <strong>par lame</strong>&nbsp;: 212 lames de test entières, jamais vues
  pendant l'apprentissage. La baseline (PCA à 50 composantes + régression logistique) évaluée sur le
  même protocole plafonne à une AUC de {_fr(m["baseline"]["auc"], 4)} — contre {_fr(m["auc"]["valeur"], 4)} pour MalariaNet.</p>
  <h2 class="reveal">Le modèle&nbsp;: MalariaNet</h2>
  <p class="reveal">Trois blocs convolutifs (32, 64, 128 canaux) avec normalisation par lot et MaxPool,
  suivi d'une tête dense avec décrochage. Le réseau ne compte que 62&nbsp;000 paramètres&nbsp;: il tient
  dans un conteneur de quelques mégaoctets, s'entraîne sur deux cœurs CPU et répond en moins de
  10 millisecondes. L'entraînement utilise rotations, miroirs et perturbations de luminosité,
  avec arrêt anticipé sur la perte de validation (16 époques au final). L'inférence est exportée
  au format ONNX et servie par ONNXRuntime&nbsp;: aucune dépendance PyTorch en démonstration.</p>
  <h2 class="reveal">Le garde-fou d'entrée</h2>
  <p class="reveal">Un classifieur à deux classes répond toujours quelque chose — y compris à une photo
  de chat. PaluScan refuse donc de diagnostiquer ce qui n'est pas un frottis&nbsp;: chaque image est
  comparée, après redimensionnement à 96×96, à un dôme de couleur ajusté sur 160 cellules du corpus
  (distance de Mahalanobis dans l'espace HSV), puis à cinq contrôles&nbsp;: présence de teintes saturées,
  grain de coloration, bords nets de l'objet, matière dense et part de fond pâle. Sur le banc d'essai,
  316 des 320 cellules du corpus sont acceptées — les quatre refusées proviennent d'un microscope de
  coloration atypique — et 76 des 78 contre-exemples sont refusés&nbsp;: 24 photos naturelles et 54
  recolorages adverses plaçant leur palette dans la bande Giemsa. Les deux survivants sont une même
  photo sombre recolorée&nbsp;: un usager déterminé peut encore tromper le contrôle, mais une photo,
  une capture d'écran ou un document passant par erreur restent l'exception plutôt que la règle.</p>
  <h2 class="reveal">La statistique, sans boîte noire</h2>
  <p class="reveal">Le seuil de décision n'est pas 0,5 par défaut mais celui de Youden
  ({_fr(m["seuil_youden"], 4)}), qui maximise sensibilité + spécificité − 1 sur le jeu de validation.
  Les intervalles binomiaux exacts sont remplacés par l'approximation de Wilson, robuste aux petits
  effectifs&nbsp;; l'AUC et son IC95 proviennent d'un bootstrap à 10&nbsp;000 rééchantillonnages
  stratifiés par lame. Le test de McNemar apparié vérifie que l'écart avec la baseline est
  significatif (p &lt; 0,001). Tout est implémenté à la main dans un unique module NumPy.</p>
  <h2 class="reveal">L'explicabilité par occlusion</h2>
  <p class="reveal">Pour chaque prédiction, une fenêtre 8×8 pixels parcourt l'image avec un pas de 4&nbsp;;
  à chaque position, on mesure la chute du logit de la classe prédite. Les régions dont le masquage
  détruit la confiance sont celles qui portent l'information discriminante. La carte obtenue,
  normalisée et superposée en dégradé rouge-jaune, permet de vérifier d'un coup d'œil que le modèle
  regarde le parasite — et non un artefact de coloration.</p>
  <h2 class="reveal">Limites assumées</h2>
  <p class="reveal">Le corpus ne contient que des cellules déjà recadrées&nbsp;: en conditions réelles,
  il faudrait en amont une segmentation de l'échantillon. Quelques « saines » sont des globules blancs,
  ce qui dégrade légèrement la spécificité mesurée. Le modèle a été entraîné sur un seul terrain de
  coloration&nbsp;: une généralisation à d'autres microscopes exigerait une validation externe — les
  quatre cellules refusées du banc d'essai en sont l'illustration directe. Enfin, PaluScan est un outil
  d'aide et de pédagogie — la lecture d'un frottis reste l'affaire d'un biologiste.</p>
</div></section>"""
    chronologie = """
<section class="section" style="padding-top:0"><div class="container">
  <div class="section-head reveal">
    <p class="kicker">Chronologie</p>
    <h2 class="section-title">Un mois, cinq étapes</h2>
  </div>
  <div class="timeline">
    <div class="timeline-item reveal"><time>Semaine 1</time><h3>Cadrage et données</h3>
      <p>Audit du corpus NIH, choix du découpage par lame, script de préparation reproductible.</p></div>
    <div class="timeline-item reveal"><time>Semaine 2</time><h3>Baseline et protocole</h3>
      <p>Régression logistique sur PCA comme plancher de référence, écriture du module statistique
      (Wilson, bootstrap, McNemar).</p></div>
    <div class="timeline-item reveal"><time>Semaine 3</time><h3>MalariaNet</h3>
      <p>Conception du CNN léger, augmentation, entraînement avec arrêt anticipé, export ONNX.</p></div>
    <div class="timeline-item reveal"><time>Semaine 4</time><h3>Évaluation et explicabilité</h3>
      <p>Courbes ROC et calibration, cartes d'occlusion, comparaison statistique avec la baseline.</p></div>
    <div class="timeline-item reveal"><time>Semaine 4 — fin</time><h3>Produit</h3>
      <p>Application FastHTML, garde-fou d'entrée, conteneurisation, déploiement de démonstration
      et documentation.</p></div>
  </div>
</div></section>"""
    corps = dashboard + prose + chronologie
    return _page_base("Méthode & résultats — PaluScan", "methode", corps, m)
