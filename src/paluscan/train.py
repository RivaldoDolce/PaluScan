"""Entraînement du CNN : boucle manuelle, arrêt anticipé et historique complet.

Usage : uv run python -m paluscan.train --epochs 12 --batch-size 64
"""

from __future__ import annotations

import argparse
import json
import time

import numpy as np
import torch
from torch.utils.data import DataLoader

from .config import RAW_DIR, REPORTS_DIR, SEED, TORCH_PATH
from .data import discover, grouped_split
from .dataset import MalariaDataset
from .model import MalariaNet
from .stats import auc_mann_whitney


def evaluate_model(model: MalariaNet, loader: DataLoader) -> tuple[float, float, float, np.ndarray, np.ndarray]:
    """Renvoie perte, exactitude, AUC, scores et étiquettes sur un lot de validation."""
    criterion = torch.nn.CrossEntropyLoss()
    model.eval()
    total_loss, correct = 0.0, 0
    scores, labels = [], []
    with torch.no_grad():
        for x, y in loader:
            logits = model(x)
            total_loss += criterion(logits, y).item() * len(y)
            correct += int((logits.argmax(1) == y).sum())
            scores.append(torch.softmax(logits, dim=1)[:, 1].numpy())
            labels.append(y.numpy())
    n = len(loader.dataset)
    scores = np.concatenate(scores)
    labels = np.concatenate(labels)
    return total_loss / n, correct / n, auc_mann_whitney(scores, labels), scores, labels


def train(args: argparse.Namespace) -> None:
    """Entraîne le réseau avec découpage par lame et conserve le meilleur point."""
    torch.manual_seed(SEED)
    torch.set_num_threads(2)

    records = discover(RAW_DIR)
    train_rec, val_rec, test_rec = grouped_split(records)
    print(f"Cellules — entraînement {len(train_rec)}, validation {len(val_rec)}, test {len(test_rec)}")
    print(f"Lames — entraînement {len({r.slide for r in train_rec})}, "
          f"validation {len({r.slide for r in val_rec})}, test {len({r.slide for r in test_rec})}")

    if args.max_train and len(train_rec) > args.max_train:
        rng = np.random.default_rng(SEED)
        idx = rng.choice(len(train_rec), size=args.max_train, replace=False)
        train_rec = [train_rec[i] for i in idx]
        print(f"Sous-ensemble d'entraînement réduit à {len(train_rec)} cellules")

    train_set = MalariaDataset(train_rec, train=True, seed=SEED)
    val_set = MalariaDataset(val_rec)
    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_set, batch_size=args.batch_size, num_workers=2)

    model = MalariaNet()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    criterion = torch.nn.CrossEntropyLoss()

    history: list[dict] = []
    best_auc = -1.0
    patience_left = args.patience

    for epoch in range(1, args.epochs + 1):
        model.train()
        running_loss, correct, seen = 0.0, 0, 0
        started = time.perf_counter()
        for x, y in train_loader:
            optimizer.zero_grad()
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * len(y)
            correct += int((logits.argmax(1) == y).sum())
            seen += len(y)
        scheduler.step()

        val_loss, val_acc, val_auc, _, _ = evaluate_model(model, val_loader)
        history.append(
            {
                "epoch": epoch,
                "train_loss": running_loss / seen,
                "train_acc": correct / seen,
                "val_loss": val_loss,
                "val_acc": val_acc,
                "val_auc": val_auc,
                "seconds": round(time.perf_counter() - started, 1),
            }
        )
        entry = history[-1]
        print(
            f"Époque {epoch:02d} | perte {entry['train_loss']:.4f} | acc {entry['train_acc']:.4f} | "
            f"val acc {val_acc:.4f} | val AUC {val_auc:.4f} | {entry['seconds']:.0f} s"
        )

        if val_auc > best_auc:
            best_auc = val_auc
            patience_left = args.patience
            torch.save({"state_dict": model.state_dict(), "epoch": epoch, "val_auc": val_auc}, TORCH_PATH)
            print(f"    meilleur point sauvegardé (AUC {val_auc:.4f})")
        else:
            patience_left -= 1
            if patience_left == 0:
                print("Arrêt anticipé : plus d'amélioration de l'AUC de validation.")
                break

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    print(f"Historique écrit dans {REPORTS_DIR / 'history.json'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Entraînement de PaluScan")
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--patience", type=int, default=4)
    parser.add_argument("--max-train", type=int, default=0, help="plafonne le nombre de cellules d'entraînement")
    return parser.parse_args()


if __name__ == "__main__":
    train(parse_args())
