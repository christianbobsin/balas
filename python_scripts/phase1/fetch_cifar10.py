import argparse
from pathlib import Path
import tarfile
from urllib.request import urlretrieve
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python_scripts.config import repo_root
from python_scripts.phase1.common import dataset_root_from_config, load_phase1_config


DEFAULT_URL = "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"
REQUIRED_FILES = [
    "data_batch_1",
    "data_batch_2",
    "data_batch_3",
    "data_batch_4",
    "data_batch_5",
    "test_batch",
    "batches.meta",
]


def validate_dataset_root(dataset_root: Path) -> None:
    missing = [name for name in REQUIRED_FILES if not (dataset_root / name).exists()]
    if missing:
        raise FileNotFoundError(f"CIFAR-10 extraction is incomplete in {dataset_root}. Missing: {missing}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download and extract the official CIFAR-10 Python archive.",
    )
    parser.add_argument("--config", help="Optional path to the phase 1 JSON config")
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help="Dataset URL. Default: official CIFAR-10 Python archive",
    )
    parser.add_argument(
        "--archive-path",
        help="Optional archive path. Defaults to datasets/downloads/cifar-10-python.tar.gz",
    )
    parser.add_argument(
        "--dataset-root",
        help="Optional extraction root. Defaults to the path in the phase 1 config.",
    )
    args = parser.parse_args()

    config, _ = load_phase1_config(args.config)
    archive_path = (
        Path(args.archive_path).resolve()
        if args.archive_path
        else (repo_root() / "datasets" / "downloads" / "cifar-10-python.tar.gz").resolve()
    )
    dataset_root = Path(args.dataset_root).resolve() if args.dataset_root else dataset_root_from_config(config)

    if dataset_root.exists():
        validate_dataset_root(dataset_root)
        print(f"CIFAR-10 already available at: {dataset_root}")
        return

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    dataset_root.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading CIFAR-10 from {args.url}")
    urlretrieve(args.url, archive_path)

    print(f"Extracting {archive_path} into {dataset_root.parent}")
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path=dataset_root.parent)

    validate_dataset_root(dataset_root)
    print(f"CIFAR-10 available at: {dataset_root}")


if __name__ == "__main__":
    main()
