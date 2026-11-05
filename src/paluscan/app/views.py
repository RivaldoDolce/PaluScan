"""Construction des pages HTML : mise en page commune, accueil, démonstration, méthode."""

from __future__ import annotations

import json
from xml.sax.saxutils import escape

from fastcore.xml import NotStr

EXEMPLES = [
    ("para_C59P20thinF_IMG_20150803_113430_cell_22.png", "Cellule parasitée"),
    ("para_C66P27N_ThinF_IMG_20150818_163419_cell_195.png", "Cellule parasitée"),
    ("para_C74P35_ThinF_IMG_20150815_113951_cell_132.png", "Cellule parasitée"),
    ("para_C95P56ThinF_IMG_20150821_172607_cell_95.png", "Cellule parasitée"),
    ("para_C99P60ThinF_IMG_20150918_141129_cell_107.png", "Cellule parasitée"),
    ("para_C99P60ThinF_IMG_20150918_141314_cell_138.png", "Cellule parasitée"),
    ("unin_C100P61ThinF_IMG_20150918_145938_cell_154.png", "Cellule saine"),
    ("unin_C125P86ThinF_IMG_20151004_102053_cell_26.png", "Cellule saine"),
    ("unin_C209ThinF_IMG_20151029_160721_cell_163.png", "Cellule saine"),
]

ESP = "\u202f"


def _fr(v: float, dec: int = 1) -> str:
    """Format décimal français avec espace insécable avant le signe %."""
    texte = f"{v:.{dec}f}".replace(".", ",")
    return texte.replace(" ", ESP)


def _pct(v: float, dec: int = 1) -> str:
    return f"{_fr(v * 100, dec)}{ESP}%"


def _icon(trait: str, classe: str = "") -> NotStr:
    return NotStr(
        f'<svg class="{classe}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{trait}</svg>'
    )


ICONE_MARQUE = '<circle cx="12" cy="12" r="8.2"/><path d="M8.4 13.6a4.6 4.6 0 0 0 7.2-1.4"/>'
ICONE_DEPOT = '<path d="M12 15V4m0 0 4 4m-4-4L8 8"/><path d="M4.5 20h15"/>'
ICONE_LOUPE = '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.4 15.4 4.2 4.2"/>'
ICONE_ALERTE = '<path d="M12 9.2v3.8m0 3.6h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/>'
ICONE_ŒIL = (
    '<path d="M2.2 12S5.8 5.6 12 5.6 21.8 12 21.8 12 18.2 18.4 12 18.4 2.2 12 2.2 12Z"/>'
    '<circle cx="12" cy="12" r="2.7"/>'
)
ICONE_BOUCLIER = '<path d="M12 3l7 2.8V11c0 4.5-3 8.5-7 10-4-1.5-7-5.5-7-10V5.8Z"/><path d="m9 11.6 2.1 2.1L15 9.5"/>'
ICONE_SIGMA = '<path d="M17 5.5H7.4l5.2 6.5-5.2 6.5H17"/>'
ICONE_CUBE = (
    '<path d="M12 2.5 3.5 7v10l8.5 4.5L20.5 17V7Z"/><path d="m3.5 7 8.5 4.5L20.5 7M12 11.5v10"/>'
)
ICONE_BASE = '<ellipse cx="12" cy="5.6" rx="7.4" ry="2.7"/><path d="M4.6 5.6v12.8c0 1.5 3.3 2.7 7.4 2.7s7.4-1.2 7.4-2.7V5.6M4.6 12c0 1.5 3.3 2.7 7.4 2.7s7.4-1.2 7.4-2.7"/>'
ICONE_ERLEN = '<path d="M9.2 3h5.6M10.2 3v5.3L4.9 17a2.4 2.4 0 0 0 2.2 3.6h9.8a2.4 2.4 0 0 0 2.2-3.6L13.8 8.3V3"/>'
ICONE_GRAPH = '<path d="M4 4.5v15h16"/><path d="m7 14 3.4-4.2 3 2.6L18.4 7"/>'


def _nav(active: str) -> str:
    liens = {"accueil": "Accueil", "demo": "Démonstration", "methode": "Méthode"}
    items = "".join(
        f'<a href="/{ancre if ancre != "accueil" else ""}" class="{"is-active" if ancre == active else ""}">{libelle}</a>'
        for ancre, libelle in liens.items()
    )
    return f'<div class="container nav-inner"><a href="/" class="brand"><span class="brand-mark">{_icon(ICONE_MARQUE)}</span><span>PaluScan<small>Vision par ordinateur · Hématologie</small></span></a><nav class="nav-links" aria-label="Navigation principale">{items}</nav><a href="/demo" class="nav-cta">Analyser une cellule</a></div>'


def _pied() -> str:
    return (
        '<footer class="footer"><div class="container footer-inner">'
        "<p>PaluScan — projet d'étude de vision par ordinateur, sans visée diagnostique.</p>"
        '<div class="footer-links"><a href="/demo">Démonstration</a><a href="/methode">Méthode</a>'
        '<a href="https://github.com" target="_blank" rel="noopener">Code source</a></div>'
        "<p>Données : NIH / LSHTM · Licence CC BY 4.0</p>"
        "</div></footer>"
    )


def _champ_microscopique() -> str:
    cellules = [
        ("core", 24, 30, 20, "18s", "-26px", "14px"),
        ("clean", 52, 22, 30, "24s", "20px", "-18px"),
        ("clean", 14, 62, 16, "29s", "-14px", "-22px"),
        ("core", 63, 58, 24, "21s", "16px", "20px"),
        ("clean", 33, 78, 22, "26s", "-20px", "12px"),
        ("core", 76, 34, 15, "19s", "12px", "-24px"),
        ("clean", 8, 44, 13, "31s", "22px", "10px"),
        ("clean", 44, 10, 18, "27s", "-18px", "20px"),
        ("core", 36, 52, 12, "23s", "24px", "-12px"),
        ("clean", 70, 74, 14, "25s", "-10px", "-16px"),
        ("core", 20, 16, 11, "22s", "10px", "22px"),
        ("clean", 84, 50, 10, "28s", "-22px", "-8px"),
    ]
    html = []
    for i, (genre, x, y, taille, duree, dx, dy) in enumerate(cellules):
        couleur = "rgba(242,84,91,0.75)" if genre == "core" else "rgba(45,212,167,0.6)"
        html.append(
            f'<span class="cell {genre}" style="left:{x}%;top:{y}%;width:{taille}%;height:{taille}%;'
            f'--c:{couleur};--dur:{duree};--dx:{dx};--dy:{dy};animation-delay:{-i * 1.7:.1f}s"></span>'
        )
    return f'<div class="field tilt" data-tilt aria-hidden="true">{"".join(html)}<span class="ring-scan"></span><span class="glare"></span></div>'


def _strip_chiffres(m: dict) -> str:
    valeurs = [
        (_fr(m["auc"]["valeur"], 4), "AUC ROC (jeu de test)"),
        (_pct(m["sensibilite"]["valeur"]), "Sensibilité"),
        (_pct(m["specificite"]["valeur"]), "Spécificité"),
        (_ent(m["n_test"]), "Cellules de test"),
    ]
    corps = "".join(
        f'<div class="stat rise" style="--rise-delay:{i * 90}ms"><div class="stat-value">{v}</div>'
        f'<div class="stat-label">{libelle}</div></div>'
        for i, (v, libelle) in enumerate(valeurs)
    )
    return f'<div class="container section"><div class="stats-strip">{corps}</div></div>'


def _page_base(titre: str, active: str, corps: str, metriques: dict) -> NotStr:
    description = (
        "PaluScan : détection du paludisme sur frottis sanguins par un réseau "
        "convolutif léger, avec explicabilité par occlusion et statistique inférentielle."
    )
    head = (
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{escape(titre)}</title>"
        f'<meta name="description" content="{description}">'
        '<link rel="icon" href="/static/img/favicon.svg" type="image/svg+xml">'
        '<link rel="preload" href="/static/fonts/fraunces-var.woff2" as="font" type="font/woff2" crossorigin>'
        '<link rel="preload" href="/static/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>'
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
    <p class="kicker rise">Vision par ordinateur · Santé publique</p>
    <h1 class="rise" style="--rise-delay:80ms">L'IA qui lit un frottis sanguin <em>comme un hématologiste</em>.</h1>
    <p class="hero-lede rise" style="--rise-delay:160ms">PaluScan examine une image microscopique de cellule sanguine
    et estime la probabilité d'infection par <em>Plasmodium</em>. Réseau convolutif léger, inférence ONNXRuntime
    sur simple processeur, décision au seuil de Youden : chaque prédiction est accompagnée de sa carte d'occlusion,
    qui montre où le modèle a porté son attention.</p>
    <div class="hero-actions rise" style="--rise-delay:240ms">
      <a href="/demo" class="btn btn-primary">{_icon(ICONE_LOUPE)} Lancer la démonstration</a>
      <a href="/methode" class="btn btn-ghost">Comprendre la méthode</a>
    </div>
    <div class="hero-badges rise" style="--rise-delay:320ms">
      <span class="chip"><span class="dot"></span>AUC 0,991 en test</span>
      <span class="chip">27 558 cellules annotées</span>
      <span class="chip">Inférence CPU &lt; 10 ms</span>
      <span class="chip">Explicabilité par occlusion</span>
    </div>
  </div>
  {_champ_microscopique()}
</div></section>"""
    pipeline = f"""
<section class="section"><div class="container">
  <div class="section-head reveal">
    <p class="kicker">Protocole</p>
    <h2 class="section-title">Trois étapes, une seule exigence&nbsp;: la rigueur.</h2>
    <p class="section-sub">Chaque décision méthodologique — découpage des données, architecture,
    statistique de test — a été prise pour produire des résultats honnêtes et reproductibles.</p>
  </div>
  <div class="grid-3">
    <article class="card card-hover tilt reveal" data-tilt style="--reveal-delay:0ms"><span class="glare"></span>
      <div class="step-num">01</div>{_icon(ICONE_BASE)}
      <h3>Données maîtrisées</h3><p>27&nbsp;558 cellules issues du jeu public NIH / LSHTM, auditées puis
      réparties <strong>par lame</strong> (212 lames de test) pour éliminer toute fuite d'information entre
      entraînement et évaluation.</p>
    </article>
    <article class="card card-hover tilt reveal" data-tilt style="--reveal-delay:120ms"><span class="glare"></span>
      <div class="step-num">02</div>{_icon(ICONE_ERLEN)}
      <h3>Apprentissage encadré</h3><p>MalariaNet, un réseau convolutif de 62&nbsp;000 paramètres, entraîné
      avec augmentation géométrique et photométrique, arrêt anticipé et suivi d'AUC par validation.</p>
    </article>
    <article class="card card-hover tilt reveal" data-tilt style="--reveal-delay:240ms"><span class="glare"></span>
      <div class="step-num">03</div>{_icon(ICONE_GRAPH)}
      <h3>Évaluation honnête</h3><p>Intervalles de Wilson, bootstrap à 10&nbsp;000 tirages, seuil de Youden,
      calibration et test de McNemar face à la baseline&nbsp;: les chiffres annoncés encadrent la performance réelle.</p>
    </article>
  </div>
</div></section>"""
    capacites = f"""
<section class="section"><div class="container">
  <div class="section-head reveal">
    <p class="kicker">Capacités</p>
    <h2 class="section-title">Un modèle qui montre son travail.</h2>
  </div>
  <div class="grid-2">
    <article class="card card-hover tilt reveal" data-tilt><span class="glare"></span>
      {_icon(ICONE_BOUCLIER)}<h3>Découpage par lame, sans fuite</h3>
      <p>Les cellules d'une même lame se ressemblent presque parfaitement. Le découpage garantit qu'aucune lame
      n'apparaît à la fois dans l'entraînement et le test — un biais classique qui gonfle artificiellement l'AUC.</p>
    </article>
    <article class="card card-hover tilt reveal" data-tilt style="--reveal-delay:120ms"><span class="glare"></span>
      {_icon(ICONE_ŒIL)}<h3>Cartes d'occlusion</h3>
      <p>En masquant des fenêtres de l'image et en mesurant la chute du logit, l'application superpose une
      carte de chaleur&nbsp;: le parasite détecté devient visible, vérifiable, contestable.</p>
    </article>
    <article class="card card-hover tilt reveal" data-tilt><span class="glare"></span>
      {_icon(ICONE_SIGMA)}<h3>Statistique écrite à la main</h3>
      <p>Wilson, bootstrap et test de McNemar sont implémentés sans dépendance lourde&nbsp;:
      le code d'évaluation tient dans un fichier, lisible ligne par ligne.</p>
    </article>
    <article class="card card-hover tilt reveal" data-tilt style="--reveal-delay:120ms"><span class="glare"></span>
      {_icon(ICONE_CUBE)}<h3>Déploiement ONNX</h3>
      <p>Le modèle est exporté au format ONNX et servi par ONNXRuntime&nbsp;: aucune dépendance PyTorch
      au moment de l'inférence, un conteneur léger, une latence de quelques millisecondes.</p>
    </article>
  </div>
</div></section>"""
    cta = """
<section class="section"><div class="container">
  <div class="card card-glass tilt reveal" data-tilt style="text-align:center;padding-block:clamp(2.5rem,6vw,4rem)">
    <span class="glare"></span>
    <h2 style="font-size:clamp(1.6rem,1.3rem+1.6vw,2.4rem)">Testez le modèle sur de vraies cellules.</h2>
    <p style="color:var(--text-2);margin-top:0.8rem">Neuf images du jeu de test sont fournies, ou importez
    vos propres frottis. L'analyse, la carte d'occlusion et le calcul de valeurs prédictives s'exécutent
    intégralement dans votre navigateur.</p>
    <div class="hero-actions" style="justify-content:center">
      <a href="/demo" class="btn btn-primary">Ouvrir le laboratoire</a>
      <a href="/methode" class="btn btn-ghost">Lire les résultats</a>
    </div>
  </div>
</div></section>"""
    corps = hero + _strip_chiffres(m) + pipeline + capacites + cta
    return _page_base("PaluScan — Détection du paludisme par IA", "accueil", corps, m)


def page_demo(m: dict) -> NotStr:
    """Page de démonstration : zone de dépôt, exemples, gabarits de résultat et de lot."""
    vignettes = "".join(
        f'<img class="thumb" src="/static/img/exemples/{nom}" alt="{alt}" loading="lazy" '
        f'data-exemple width="58" height="58">'
        for nom, alt in EXEMPLES
    )
    zone = f"""
<section class="section"><div class="container">
  <div class="section-head reveal">
    <p class="kicker">Laboratoire interactif</p>
    <h2 class="section-title">Analysez une cellule en un clic.</h2>
    <p class="section-sub">Déposez une ou plusieurs images (PNG, JPEG). Pour chaque cellule, PaluScan renvoie
    sa décision au seuil de Youden, la probabilité d'infection, la latence de mesure et la carte d'occlusion.</p>
  </div>
  <div class="analyzer">
    <div class="card reveal">
      <div class="dropzone" id="zone-depot" role="button" tabindex="0" aria-label="Déposer des images à analyser">
        <input type="file" id="entree-fichiers" accept="image/png,image/jpeg" multiple hidden>
        <div class="dropzone-icon">{_icon(ICONE_DEPOT)}</div>
        <strong>Déposez vos images ici</strong>
        <span>PNG ou JPEG · 8 Mo max · jusqu'à 12 fichiers, ou cliquez pour parcourir</span>
      </div>
      <div class="examples">
        <p class="examples-title">Exemples du jeu de test</p>
        <div class="examples-row">{vignettes}</div>
      </div>
    </div>
    <div class="card card-glass reveal" style="--reveal-delay:120ms">
      <div id="zone-resultat" class="result" aria-live="polite">
        <div class="result-empty">
          {_icon(ICONE_LOUPE)}
          <p>L'analyse apparaîtra ici.</p>
          <p style="font-size:0.85rem;margin-top:0.4rem">Importez une image ou choisissez un exemple.</p>
        </div>
      </div>
    </div>
  </div>
  <section id="section-lot" class="section" hidden style="padding-bottom:0">
    <h2 class="section-title" style="font-size:1.4rem">Analyse en lot</h2>
    <div class="table-wrap" style="margin-top:1rem">
      <table class="batch">
        <thead><tr><th>Image</th><th>Décision</th><th>P(infection)</th><th>Latence</th></tr></thead>
        <tbody id="corps-lot"></tbody>
      </table>
    </div>
  </section>
</div></section>"""
    modele_resultat = f"""
<template id="modele-resultat">
  <div class="verdict verdict-healthy" data-champ="verdict"><span class="verdict-dot"></span><span data-champ="verdict-libelle">Saine</span></div>
  <div class="gauge-wrap" style="margin-top:1.3rem">
    <div class="gauge">
      <svg viewBox="0 0 172 172" width="172" height="172" role="img" aria-label="Probabilité d'infection">
        <defs><linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#f2545b"/><stop offset="100%" stop-color="#ff8a5c"/>
        </linearGradient></defs>
        <circle class="gauge-track" cx="86" cy="86" r="76"/>
        <circle class="gauge-fill" cx="86" cy="86" r="76" stroke-dasharray="477.5" stroke-dashoffset="477.5"/>
      </svg>
      <div class="gauge-center"><div class="gauge-value" data-champ="pourcentage">0%</div>
      <div class="gauge-caption">probabilité d'infection</div></div>
    </div>
    <div class="prob-bars">
      <div class="prob-row"><div class="prob-head"><span>Parasitée</span><span data-champ="p-infectee">—</span></div>
        <div class="prob-track"><div class="prob-fill infected" data-champ="barre-infectee"></div></div></div>
      <div class="prob-row"><div class="prob-head"><span>Saine</span><span data-champ="p-sain">—</span></div>
        <div class="prob-track"><div class="prob-fill healthy" data-champ="barre-sain"></div></div></div>
      <div class="result-meta" style="margin-top:0.2rem">
        <span class="tag tag-muted" data-champ="meta-latence">latence —</span>
        <span class="tag tag-muted" data-champ="meta-seuil">seuil de Youden —</span>
        <span class="tag tag-muted">ONNXRuntime · CPU</span>
      </div>
    </div>
  </div>
  <div class="gauge-wrap" style="margin-top:1.4rem">
    <div class="scan-visual is-scanning" data-champ="conteneur-visual">
      <img data-champ="apercu" src="" alt="Cellule analysée" width="148" height="148">
      <img data-champ="carte" src="" alt="Carte d'occlusion superposée" width="148" height="148"
           style="position:absolute;inset:0;opacity:1;transition:opacity .35s">
      <span class="scan-sweep"></span>
    </div>
    <div>
      <button type="button" class="toggle is-on" data-champ="bouton-carte" aria-pressed="true">
        <span class="knob"></span> Carte d'occlusion
      </button>
      <p class="ppv-note" style="margin-top:0.6rem">La carte signale les régions dont le masquage réduit le plus
      la confiance du modèle — le parasite détecté apparaît en rouge.</p>
    </div>
  </div>
  <div class="slider-block">
    <div class="slider-head"><span>Prévalence locale du paludisme</span><span class="slider-value" data-champ="valeur-prevalence">1,0%</span></div>
    <input type="range" min="0.1" max="40" step="0.1" value="1" data-champ="curseur-prevalence" aria-label="Prévalence locale">
    <div class="ppv-grid">
      <div class="ppv-cell pos"><div class="ppv-label">VPP · prédire infecté</div><div class="ppv-value" data-champ="vpp">—</div></div>
      <div class="ppv-cell neg"><div class="ppv-label">VPN · prédire sain</div><div class="ppv-value" data-champ="vpn">—</div></div>
    </div>
    <p class="ppv-note">Valeurs prédictives recalculées par la règle de Bayes à partir de la sensibilité
    ({_pct(m.get("sensibilite", {}).get("valeur", 0.9677))}) et de la spécificité
    ({_pct(m.get("specificite", {}).get("valeur", 0.9541))}) mesurées sur le jeu de test.</p>
  </div>
</template>"""
    modele_ligne = """
<template id="modele-ligne-lot">
  <tr><td><img class="cell-mini" src="" alt="" width="44" height="44"></td>
  <td><span class="tag tag-muted">—</span></td><td>—</td><td>—</td></tr>
</template>"""
    corps = zone + modele_resultat + modele_ligne
    return _page_base("Démonstration — PaluScan", "demo", corps, m)


# ---------- Graphiques SVG (chaînes brutes : attributs viewBox/linearGradient camelCase) ----------

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
            f'<line x1="{x:.1f}" y1="{Y0}" x2="{x:.1f}" y2="{Y0 + HAUTEUR_PLOT}" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>'
            f'<line x1="{X0}" y1="{y:.1f}" x2="{X0 + LARGEUR_PLOT}" y2="{y:.1f}" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>'
            f'<text x="{x:.1f}" y="{Y0 + HAUTEUR_PLOT + 16}" font-size="10" fill="#727d92" text-anchor="middle">{libelle}</text>'
            f'<text x="{X0 - 7}" y="{y + 3:.1f}" font-size="10" fill="#727d92" text-anchor="end">{libelle}</text>'
        )
    return traits


def _courbe(
    xs: list[float], ys: list[float], classe: str, couleur: str = "", delai: int = 0
) -> str:
    points = " ".join(
        f"{X0 + x * LARGEUR_PLOT:.1f},{Y0 + (1 - y) * HAUTEUR_PLOT:.1f}"
        for x, y in zip(xs, ys, strict=False)
    )
    style = (
        f' style="stroke:{couleur};animation-delay:{delai}ms"'
        if couleur
        else f' style="animation-delay:{delai}ms"'
    )
    return f'<polyline class="{classe}" points="{points}"{style}/>'


def _svg(titre: str, sous_texte: str, contenu: str, etiquette: str = "") -> str:
    return f"""
<div class="card chart-card">
  <div class="chart-title"><h3>{titre}</h3><span>{sous_texte}</span></div>
  <svg class="chart-svg" viewBox="0 0 {LARG} {HAUT}" role="img" aria-label="{escape(etiquette or titre)}">
    {_cadre()}{contenu}
  </svg>
</div>"""


def _carte_roc(m: dict) -> str:
    roc = m["roc"]
    courbe = _courbe(roc["fpr"], roc["tpr"], "chart-line")
    diagonale = _courbe([0, 1], [0, 1], "chart-line alt")
    return _svg(
        "Courbe ROC",
        f"AUC {_fr(m['auc']['valeur'], 4)} · IC95 {_fr(m['auc']['ic95'][0], 3)}–{_fr(m['auc']['ic95'][1], 3)}",
        courbe + diagonale,
    )


def _carte_pr(m: dict) -> str:
    pr = m["pr"]
    courbe = _courbe(pr["rappel"], pr["precision"], "chart-line", delai=150)
    return _svg("Précision–rappel", f"Précision moyenne {_fr(m['precision_moyenne'], 4)}", courbe)


def _carte_calibration(m: dict) -> str:
    cal = m["calibration"]
    diagonale = _courbe([0, 1], [0, 1], "chart-line alt")
    points = "".join(
        f'<circle cx="{X0 + c * LARGEUR_PLOT:.1f}" cy="{Y0 + (1 - o) * HAUTEUR_PLOT:.1f}" r="3.4" '
        f'fill="#f2545b" stroke="#07090f" stroke-width="1.4"/>'
        for c, o in zip(cal["confiance"], cal["observe"], strict=False)
    )
    segment = _courbe(cal["confiance"], cal["observe"], "chart-line", delai=250)
    return _svg("Calibration", "Observé contre prédit (10 classes)", diagonale + segment + points)


def _carte_perte(m: dict) -> str:
    e = m["entrainement"]
    n = len(e["epoques"])
    x_train = [i / (n - 1) for i in range(n)]
    y_max = max(max(e["perte_train"]), max(e["perte_val"])) * 1.08
    train = _courbe(x_train, [v / y_max for v in e["perte_train"]], "chart-line")
    val = _courbe(
        x_train, [v / y_max for v in e["perte_val"]], "chart-line", couleur="#7db2ff", delai=200
    )
    legende = (
        '<span style="display:inline-flex;align-items:center;gap:0.4rem">'
        '<i style="width:14px;height:2.5px;background:var(--carmin)"></i>entraînement</span>'
        '<span style="display:inline-flex;align-items:center;gap:0.4rem">'
        '<i style="width:14px;height:2.5px;background:#7db2ff"></i>validation</span>'
    )
    return f"""
<div class="card chart-card">
  <div class="chart-title"><h3>Perte par époque</h3><span style="display:flex;gap:0.9rem">{legende}</span></div>
  <svg class="chart-svg" viewBox="0 0 {LARG} {HAUT}" role="img" aria-label="Évolution de la perte d'entraînement et de validation">
    {_cadre()}{train}{val}
  </svg>
</div>"""


def _carte_confusion(m: dict) -> str:
    c = m["matrice_confusion"]

    def cellule(nombre: int, sous: str, classe: str) -> str:
        return (
            f'<div class="conf-cell {classe}"><span class="big">{nombre}</span>'
            f'<span class="sub">{sous}</span></div>'
        )

    entete = '<div></div><div class="conf-head">Prédit · infecté</div><div class="conf-head">Prédit · sain</div>'
    return f"""
<div class="card chart-card">
  <div class="chart-title"><h3>Matrice de confusion</h3><span>Seuil de Youden {_fr(m["seuil_youden"], 4)}</span></div>
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
        band = f"left:{gauche * 100:.1f}%;width:{(droite - gauche) * 100:.1f}%;animation-delay:{i * 120}ms"
        dot = f"left:{v['valeur'] * 100:.1f}%"
        lignes += (
            f'<div class="ci-row"><span>{nom}</span>'
            f'<span class="ci-track"><span class="ci-band" style="{band}"></span>'
            f'<span class="ci-dot" style="{dot}"></span></span>'
            f"<span>{_pct(gauche, 1)} – {_pct(droite, 1)}</span></div>"
        )
    return f"""
<div class="card chart-card">
  <div class="chart-title"><h3>Intervalles de confiance à 95{ESP}%</h3><span>{_ent(m["n_test"])} cellules · {m["n_test_slides"]} lames</span></div>
  {lignes}
</div>"""


def _carte_baseline(m: dict) -> str:
    b = m["baseline"]
    mc = m["mcnemar"]

    def barre(valeur: float, couleur: str, delai: int) -> str:
        return (
            f'<div class="prob-track" style="margin-top:0.45rem"><div class="prob-fill" '
            f'style="width:{valeur * 100:.1f}%;background:{couleur};transition-delay:{delai}ms"></div></div>'
        )

    return f"""
<div class="card chart-card">
  <div class="chart-title"><h3>Contre la baseline</h3><span>Test de McNemar</span></div>
  <div style="font-size:0.88rem">
    <div class="prob-head" style="display:flex;justify-content:space-between"><span>MalariaNet (CNN)</span><strong>AUC {_fr(m["auc"]["valeur"], 4)}</strong></div>
    {barre(m["auc"]["valeur"], "linear-gradient(90deg,#b3282f,var(--carmin))", 100)}
    <div class="prob-head" style="display:flex;justify-content:space-between;margin-top:1rem"><span>{escape(b["nom"])}</span><strong>AUC {_fr(b["auc"], 4)}</strong></div>
    {barre(b["auc"], "rgba(255,255,255,0.22)", 250)}
  </div>
  <p class="ppv-note">Sur les {_ent(mc["n_discordantes"])} cellules tranchées différemment, la baseline se trompe seule
  {_ent(mc["b_base_seulement"])} fois contre {_ent(mc["c_cnn_seulement"])} pour le CNN (p &lt; 0,001)&nbsp;: l'écart est
  significatif, pas un artefact d'échantillonnage.</p>
</div>"""


def _ent(v: int) -> str:
    """Format entier français : espace fine insécable entre les milliers."""
    return f"{v:,}".replace(",", ESP)


def page_methode(m: dict) -> NotStr:
    """Page méthode : tableau de bord graphique, prose rédigée et chronologie."""
    dashboard = f"""
<section class="section" style="padding-top:0"><div class="container">
  <div class="section-head reveal">
    <p class="kicker">Résultats</p>
    <h2 class="section-title">Ce que dit le jeu de test.</h2>
    <p class="section-sub">Aucune métrique isolée&nbsp;: chaque chiffre est accompagné de son intervalle
    de confiance, de la courbe qui le justifie et du test statistique qui le confronte à la baseline.</p>
  </div>
  <div class="grid-2">
    {_carte_roc(m)}{_carte_calibration(m)}
    {_carte_perte(m)}{_carte_confusion(m)}
    {_carte_intervalles(m)}{_carte_baseline(m)}
  </div>
  <div class="grid-2" style="margin-top:1.1rem">{_carte_pr(m)}</div>
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
  avec arrêt anticipé sur la perte de validation (16 époques au final).</p>
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
  coloration&nbsp;: une généralisation à d'autres microscopes exigerait une validation externe. Enfin,
  PaluScan est un outil d'aide et de pédagogie — la lecture d'un frottis reste l'affaire d'un
  biologiste.</p>
</div></section>"""
    chronologie = """
<section class="section" style="padding-top:0"><div class="container">
  <div class="section-head reveal">
    <p class="kicker">Chronologie</p>
    <h2 class="section-title">Un mois, cinq étapes.</h2>
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
      <p>Application FastHTML, conteneurisation, déploiement de démonstration et documentation.</p></div>
  </div>
</div></section>"""
    corps = dashboard + prose + chronologie
    return _page_base("Méthode & résultats — PaluScan", "methode", corps, m)
