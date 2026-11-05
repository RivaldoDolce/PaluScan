"""Application FastHTML de PaluScan."""

from __future__ import annotations

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
    """Lancement du serveur (port 7860, conforme aux Spaces Hugging Face)."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)
