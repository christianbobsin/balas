import argparse
import json
import os
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python_scripts.config import default_serial_port
from python_scripts.phase1.common import artifact_root_from_config, load_phase1_config


def relative_to_manifest_or_absolute(path: Path, manifest_dir: Path) -> str:
    try:
        return os.path.relpath(path.resolve(), manifest_dir.resolve())
    except Exception:
        return str(path.resolve())


def load_json(path: Path) -> dict | list:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a benchmark suite manifest for the generated image classification models.",
    )
    parser.add_argument("--config", help="Optional path to the phase 1 JSON config")
    parser.add_argument(
        "--quantized-manifest",
        help="Optional path to the quantized model manifest. Defaults to <artifact_root>/quantized_models/manifest.json",
    )
    parser.add_argument(
        "--dataset-dir",
        help="Optional profiling dataset directory. Defaults to <artifact_root>/profiling_dataset/default",
    )
    parser.add_argument(
        "--output-path",
        help="Optional output path. Defaults to <artifact_root>/manifests/image-classification-suite.json",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Include only the first N quantized models",
    )
    parser.add_argument(
        "--skip-compile",
        action="store_true",
        help="Set skip_compile=true in the manifest defaults",
    )
    parser.add_argument(
        "--skip-deploy",
        action="store_true",
        help="Set skip_deploy=true in the manifest defaults",
    )
    parser.add_argument(
        "--serial-device",
        default=default_serial_port(),
        help="Serial device to place in manifest defaults",
    )
    args = parser.parse_args()

    config, _ = load_phase1_config(args.config)
    artifact_root = artifact_root_from_config(config)
    quantized_manifest = (
        Path(args.quantized_manifest).resolve()
        if args.quantized_manifest
        else artifact_root / "quantized_models" / "manifest.json"
    )
    dataset_dir = (
        Path(args.dataset_dir).resolve()
        if args.dataset_dir
        else artifact_root / "profiling_dataset" / "default"
    )
    output_path = (
        Path(args.output_path).resolve()
        if args.output_path
        else artifact_root / "manifests" / "image-classification-suite.json"
    )
    manifest_dir = output_path.parent.resolve()

    quantized_entries = load_json(quantized_manifest)
    if args.limit is not None:
        quantized_entries = quantized_entries[: args.limit]
    if not quantized_entries:
        raise ValueError("No quantized models were selected")

    manifest = {
        "suite_name": "phase1-image-classification",
        "defaults": {
            "serial_device": args.serial_device,
            "skip_compile": args.skip_compile,
            "skip_deploy": args.skip_deploy,
        },
        "entries": [],
    }

    for entry in quantized_entries:
        manifest["entries"].append(
            {
                "family": entry["family"],
                "name": entry["name"],
                "model_path": relative_to_manifest_or_absolute(Path(entry["tflite_path"]), manifest_dir),
                "profiling_dataset": relative_to_manifest_or_absolute(dataset_dir, manifest_dir),
            },
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Suite manifest written to {output_path}")


if __name__ == "__main__":
    main()
