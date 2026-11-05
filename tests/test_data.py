"""Découpage groupé par lame : aucune lame ne doit chevaucher deux lots."""

from pathlib import Path

from paluscan.data import CellRecord, grouped_split, slide_id


def _fausses_cellules(lames_par_classe: int = 6, cellules_par_lame: int = 4):
    records = []
    for classe, nom in enumerate(["Parasitized", "Uninfected"]):
        for lame in range(lames_par_classe):
            for cellule in range(cellules_par_lame):
                stem = f"C{lame}P{lame}_ThinF_IMG_20250101_100{cellule}_cell_{cellule}"
                records.append(
                    CellRecord(path=Path(nom) / f"{stem}.png", label=classe, slide=slide_id(stem))
                )
    return records


def test_slide_id_extrait_la_lame():
    stem = "C33P1thinF_IMG_20150819_114731_cell_10"
    assert slide_id(stem) == "C33P1thinF_IMG_20150819_114731"
    assert slide_id("nom_inconnu") == "nom_inconnu"


def test_grouped_split_couvre_toutes_les_cellules():
    records = _fausses_cellules()
    train, val, test = grouped_split(records)
    assert len(train) + len(val) + len(test) == len(records)
    assert train and val and test


def test_grouped_split_aucune_fuite_de_lame():
    records = _fausses_cellules()
    train, val, test = grouped_split(records)
    lames_train = {r.slide for r in train}
    lames_val = {r.slide for r in val}
    lames_test = {r.slide for r in test}
    assert not (lames_train & lames_val)
    assert not (lames_train & lames_test)
    assert not (lames_val & lames_test)


def test_grouped_split_est_deterministe():
    records = _fausses_cellules()
    premier = grouped_split(records)
    second = grouped_split(records)
    assert [[r.path for r in lot] for lot in premier] == [[r.path for r in lot] for lot in second]


def test_grouped_split_proportions():
    records = _fausses_cellules()
    train, val, test = grouped_split(records, train_frac=0.70, val_frac=0.15)
    total = len(records)
    assert len(train) / total >= 0.6
    assert len(test) / total >= 0.1
