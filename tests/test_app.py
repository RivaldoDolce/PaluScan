"""Application FastHTML : pages, API d'inférence et gestion d'erreurs."""

import io
from pathlib import Path

import pytest
from PIL import Image
from starlette.testclient import TestClient

from paluscan.app import create_app

EXEMPLE_PARASITE = (
    Path(__file__).resolve().parents[1]
    / "src/paluscan/app/static/img/exemples/para_C59P20thinF_IMG_20150803_113430_cell_22.png"
)
EXEMPLE_SAIN = (
    Path(__file__).resolve().parents[1]
    / "src/paluscan/app/static/img/exemples/unin_C100P61ThinF_IMG_20150918_145938_cell_154.png"
)


@pytest.fixture(scope="module")
def client():
    with TestClient(create_app()) as test_client:
        yield test_client


def _fichier_png(couleur=(150, 60, 80), taille=(64, 64)) -> bytes:
    tampon = io.BytesIO()
    Image.new("RGB", taille, couleur).save(tampon, format="PNG")
    return tampon.getvalue()


def test_pages_servees(client):
    for route, extrait in [
        ("/", "L'IA qui lit un frottis sanguin"),
        ("/demo", "Laboratoire interactif"),
        ("/methode", "Ce que dit le jeu de test"),
    ]:
        reponse = client.get(route)
        assert reponse.status_code == 200
        assert extrait in reponse.text
        assert 'lang="fr"' in reponse.text


def test_statiques_servees(client):
    assert client.get("/static/css/style.css").status_code == 200
    assert client.get("/static/js/app.js").status_code == 200
    assert client.get("/static/img/favicon.svg").status_code == 200


def test_analyser_image_parasitee(client):
    reponse = client.post(
        "/api/analyser",
        files={"image": ("cell.png", EXEMPLE_PARASITE.read_bytes(), "image/png")},
        data={"occlusion": "1"},
    )
    assert reponse.status_code == 200
    resultat = reponse.json()
    assert resultat["infectee"] is True
    assert 0 <= resultat["probabilite_infection"] <= 1
    assert resultat["carte"].startswith("data:image/png;base64,")
    assert "seuil_youden" in resultat


def test_analyser_image_saine_sans_carte(client):
    reponse = client.post(
        "/api/analyser",
        files={"image": ("cell.png", EXEMPLE_SAIN.read_bytes(), "image/png")},
        data={"occlusion": "0"},
    )
    assert reponse.status_code == 200
    resultat = reponse.json()
    assert resultat["infectee"] is False
    assert "carte" not in resultat


def test_analyser_rejette_format_inconnu(client):
    reponse = client.post(
        "/api/analyser", files={"image": ("dessin.svg", b"<svg/>", "image/svg+xml")}
    )
    assert reponse.status_code == 415
    assert "erreur" in reponse.json()


def test_analyser_sans_image(client):
    reponse = client.post("/api/analyser", data={"occlusion": "0"})
    assert reponse.status_code == 415


def test_lot_deux_images(client):
    fichiers = [
        ("images", ("a.png", EXEMPLE_PARASITE.read_bytes(), "image/png")),
        ("images", ("b.png", EXEMPLE_SAIN.read_bytes(), "image/png")),
    ]
    reponse = client.post("/api/analyser-lot", files=fichiers)
    assert reponse.status_code == 200
    resultats = reponse.json()["resultats"]
    assert len(resultats) == 2
    assert resultats[0]["infectee"] is True
    assert resultats[1]["infectee"] is False


def test_lot_limite_de_taille(client):
    contenu = _fichier_png()
    fichiers = [("images", (f"{i}.png", contenu, "image/png")) for i in range(13)]
    reponse = client.post("/api/analyser-lot", files=fichiers)
    assert reponse.status_code == 413


def test_route_inconnue_json(client):
    reponse = client.get("/route-inexistante")
    assert reponse.status_code == 404
