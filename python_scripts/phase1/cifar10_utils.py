from pathlib import Path
import pickle
import warnings

import numpy as np


META_FILE = "batches.meta"
TRAIN_BATCHES = [f"data_batch_{index}" for index in range(1, 6)]
TEST_BATCHES = ["test_batch"]


def _load_pickle(path: Path) -> dict:
    with path.open("rb") as handle:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="dtype\\(\\): align should be passed as Python or NumPy boolean.*",
                category=Warning,
            )
            return pickle.load(handle, encoding="latin1")


def _get(mapping: dict, key: str):
    if key in mapping:
        return mapping[key]
    byte_key = key.encode("utf-8")
    if byte_key in mapping:
        return mapping[byte_key]
    raise KeyError(f"Key {key!r} not found in CIFAR-10 payload")


def load_label_names(dataset_root: Path) -> list[str]:
    meta = _load_pickle(dataset_root / META_FILE)
    raw_label_names = _get(meta, "label_names")
    label_names = []
    for name in raw_label_names:
        label_names.append(name.decode("utf-8") if isinstance(name, bytes) else str(name))
    return label_names


def _load_split_batches(dataset_root: Path, batch_names: list[str]) -> tuple[np.ndarray, np.ndarray]:
    features = []
    labels = []
    for batch_name in batch_names:
        batch = _load_pickle(dataset_root / batch_name)
        raw = _get(batch, "data").reshape(-1, 3, 32, 32)
        features.append(np.transpose(raw, (0, 2, 3, 1)))
        labels.extend(_get(batch, "labels"))
    return np.concatenate(features, axis=0), np.asarray(labels, dtype=np.int64)


def load_cifar10_split(dataset_root: Path, split: str) -> tuple[np.ndarray, np.ndarray, list[str]]:
    if split == "train":
        images, labels = _load_split_batches(dataset_root, TRAIN_BATCHES)
    elif split == "test":
        images, labels = _load_split_batches(dataset_root, TEST_BATCHES)
    else:
        raise ValueError(f"Unsupported split: {split}")
    label_names = load_label_names(dataset_root)
    return images, labels, label_names
