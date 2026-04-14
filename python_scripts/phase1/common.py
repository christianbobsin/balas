import json
from itertools import product
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python_scripts.config import repo_root


DEFAULT_CONFIG_PATH = repo_root() / "configs" / "phase1_image_classification.json"
GRID_KEYS = [
    "channels_1",
    "kernel_1",
    "channels_2",
    "kernel_2",
    "channels_3",
    "kernel_3",
]


def load_phase1_config(config_path: str | None = None) -> tuple[dict, Path]:
    config_file = Path(config_path).resolve() if config_path else DEFAULT_CONFIG_PATH.resolve()
    with config_file.open("r", encoding="utf-8") as handle:
        return json.load(handle), config_file


def resolve_from_repo(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return (repo_root() / path).resolve()


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_variant_name(variant: dict) -> str:
    return (
        "ic_"
        f"c1-{variant['channels_1']}_k1-{variant['kernel_1']}_"
        f"c2-{variant['channels_2']}_k2-{variant['kernel_2']}_"
        f"c3-{variant['channels_3']}_k3-{variant['kernel_3']}"
    )


def iter_variants(config: dict) -> list[dict]:
    grid = config["grid"]
    missing = [key for key in GRID_KEYS if key not in grid]
    if missing:
        raise KeyError(f"Missing grid keys in config: {missing}")

    variants = []
    for values in product(*(grid[key] for key in GRID_KEYS)):
        variant = dict(zip(GRID_KEYS, values, strict=True))
        variant["name"] = format_variant_name(variant)
        variants.append(variant)
    return variants


def select_variants(variants: list[dict], limit: int | None, only: set[str] | None) -> list[dict]:
    selected = variants
    if only:
        selected = [variant for variant in selected if variant["name"] in only]
    if limit is not None:
        selected = selected[:limit]
    return selected


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def artifact_root_from_config(config: dict) -> Path:
    return resolve_from_repo(config["paths"]["artifact_root"])


def dataset_root_from_config(config: dict) -> Path:
    return resolve_from_repo(config["paths"]["dataset_root"])


def mlcommons_root_from_config(config: dict) -> Path:
    return resolve_from_repo(config["paths"]["mlcommons_root"])
