import csv
import json
from pathlib import Path
import sys

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python_scripts.config import repo_root


def resolve_path(base_dir: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def load_suite_manifest(manifest_path: str) -> tuple[dict, Path]:
    manifest_file = Path(manifest_path).resolve()
    with manifest_file.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    return manifest, manifest_file.parent


def iter_dataset_arrays(dataset_dir: Path) -> list[tuple[str, np.ndarray]]:
    samples = []
    for sample_path in sorted(dataset_dir.glob("*.bin")):
        samples.append((sample_path.name, np.fromfile(sample_path, dtype=np.float32)))
    if not samples:
        raise FileNotFoundError(f"No .bin files were found in {dataset_dir}")
    return samples


def csv_append_row(csv_path: Path, fieldnames: list[str], row: dict) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def to_float(value: str) -> float | None:
    if value in {"", "None", None}:
        return None
    return float(value)


def to_int(value: str) -> int | None:
    if value in {"", "None", None}:
        return None
    return int(float(value))


def pearson_correlation(x_values: list[float], y_values: list[float]) -> float | None:
    if len(x_values) < 2 or len(y_values) < 2:
        return None
    x = np.asarray(x_values, dtype=np.float64)
    y = np.asarray(y_values, dtype=np.float64)
    if np.allclose(x, x[0]) or np.allclose(y, y[0]):
        return None
    return float(np.corrcoef(x, y)[0, 1])


def relative_to_repo(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root()))
    except ValueError:
        return str(path.resolve())
