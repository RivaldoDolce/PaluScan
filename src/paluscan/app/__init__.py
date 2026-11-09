"""Application FastHTML de PaluScan."""

from __future__ import annotations

import os
from pathlib import Path

from fasthtml.common import FastHTML
from starlette.staticfiles import StaticFiles

from . import routes

STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastHTML:
    """Assemble l'application : moteur d'inférence, statiques, pages et API."""
    app = FastHTML(default_hdrs=False)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    routes.monter(app)
    return app


app = create_app()


def main() -> None:
    """Lancement du serveur (port dynamique sur Render, 7860 par défaut en local et sur HF)."""
    import uvicorn

    # Récupère le port attribué par Render (ou prend 7860 si la variable n'existe pas)
    port = int(os.environ.get("PORT", 7860))

    uvicorn.run(app, host="0.0.0.0", port=port)
