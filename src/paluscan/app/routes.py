"""Routes applicatives : pages HTML et API d'inférence."""

from __future__ import annotations

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from . import views
from .core import NOMBRE_MAX_IMAGES_LOT, ErreurHorsDomaine, ErreurValidation, get_moteur


def _erreur(message: str, statut: int, motifs: list[str] | None = None) -> JSONResponse:
    charge: dict = {"erreur": message}
    if motifs:
        charge["motifs"] = motifs
    return JSONResponse(charge, status_code=statut)


def _gestionnaire_http(req: Request, exc: HTTPException):
    message = "Ressource introuvable." if exc.status_code == 404 else "Erreur de requête."
    return _erreur(message, exc.status_code)


async def _extraire(formulaire: dict, cle: str):
    fichier = formulaire.get(cle)
    if fichier is None or not getattr(fichier, "filename", ""):
        raise ErreurValidation("Aucune image reçue.")
    return fichier


def monter(app) -> None:
    """Enregistre pages et points d'accès sur l'application FastHTML."""

    @app.get("/")
    def accueil():
        return views.page_accueil(get_moteur().metriques)

    @app.get("/demo")
    def demo():
        return views.page_demo(get_moteur().metriques)

    @app.get("/methode")
    def methode():
        return views.page_methode(get_moteur().metriques)

    @app.post("/api/analyser")
    async def analyser(req: Request):
        formulaire = await req.form()
        try:
            fichier = await _extraire(formulaire, "image")
            image = get_moteur().decodage(await fichier.read())
            avec_carte = formulaire.get("occlusion") != "0"
            return get_moteur().analyser(image, avec_carte=avec_carte)
        except ErreurHorsDomaine as exc:
            return _erreur(str(exc), 422, list(exc.motifs))
        except ErreurValidation as exc:
            return _erreur(str(exc), 415)

    @app.post("/api/analyser-lot")
    async def analyser_lot(req: Request):
        formulaire = await req.form()
        fichiers = formulaire.getlist("images")
        if not fichiers:
            return _erreur("Aucune image reçue.", 415)
        if len(fichiers) > NOMBRE_MAX_IMAGES_LOT:
            return _erreur(f"Maximum {NOMBRE_MAX_IMAGES_LOT} images par lot.", 413)
        moteur = get_moteur()
        resultats = []
        for fichier in fichiers:
            try:
                image = moteur.decodage(await fichier.read())
                r = moteur.analyser(image, avec_carte=False)
                resultats.append(
                    {
                        "infectee": r["infectee"],
                        "probabilite_infection": r["probabilite_infection"],
                        "latence_ms": r["latence_ms"],
                    }
                )
            except ErreurHorsDomaine as exc:
                resultats.append({"hors_domaine": True, "motifs": list(exc.motifs)})
            except ErreurValidation as exc:
                resultats.append({"erreur": str(exc)})
        return {"resultats": resultats}

    app.exception_handlers[HTTPException] = _gestionnaire_http
