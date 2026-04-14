import argparse
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np

from python_scripts.phase1.cifar10_utils import load_cifar10_split
from python_scripts.phase1.common import (
    artifact_root_from_config,
    dataset_root_from_config,
    ensure_directory,
    load_phase1_config,
    write_json,
)


def slugify(text: str) -> str:
    return text.lower().replace(" ", "_")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the profiling dataset for the image classification phase 1 flow.",
    )
    parser.add_argument("--config", help="Optional path to the phase 1 JSON config")
    parser.add_argument(
        "--dataset-root",
        help="Optional CIFAR-10 root. Defaults to the path in the phase 1 config.",
    )
    parser.add_argument(
        "--output-dir",
        help="Optional output directory. Defaults to <artifact_root>/profiling_dataset/default",
    )
    parser.add_argument(
        "--samples-per-class",
        type=int,
        help="Override the samples-per-class value from the config",
    )
    args = parser.parse_args()

    config, _ = load_phase1_config(args.config)
    artifact_root = artifact_root_from_config(config)
    dataset_root = Path(args.dataset_root).resolve() if args.dataset_root else dataset_root_from_config(config)
    output_dir = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else artifact_root / "profiling_dataset" / "default"
    )
    ensure_directory(output_dir)

    profiling_cfg = config["profiling_dataset"]
    split = profiling_cfg.get("split", "test")
    samples_per_class = args.samples_per_class or int(profiling_cfg.get("samples_per_class", 1))
    images, labels, label_names = load_cifar10_split(dataset_root, split)

    selections = []
    written = 0
    for class_index, label_name in enumerate(label_names):
        class_positions = np.flatnonzero(labels == class_index)
        if len(class_positions) < samples_per_class:
            raise ValueError(
                f"Class {class_index} has only {len(class_positions)} samples in split {split}, "
                f"but {samples_per_class} were requested",
            )
        for sample_offset, dataset_index in enumerate(class_positions[:samples_per_class], start=1):
            image = images[int(dataset_index)].astype(np.float32)
            sample_name = f"class_{class_index:02d}_{slugify(label_name)}_{sample_offset:03d}.bin"
            sample_path = output_dir / sample_name
            image.tofile(sample_path)
            selections.append(
                {
                    "sample_name": sample_name,
                    "class_index": class_index,
                    "label_name": label_name,
                    "dataset_index": int(dataset_index),
                    "shape": list(image.shape),
                    "dtype": "float32",
                },
            )
            written += 1

    manifest = {
        "family": config["family"],
        "split": split,
        "samples_per_class": samples_per_class,
        "total_samples": written,
        "dataset_root": str(dataset_root),
        "output_dir": str(output_dir),
        "samples": selections,
    }
    write_json(output_dir / "manifest.json", manifest)
    print(f"Wrote {written} profiling samples to {output_dir}")


if __name__ == "__main__":
    main()
