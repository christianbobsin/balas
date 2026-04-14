import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python_scripts.phase1.cifar10_utils import load_cifar10_split
from python_scripts.phase1.common import (
    artifact_root_from_config,
    dataset_root_from_config,
    ensure_directory,
    load_phase1_config,
    write_json,
)


def representative_dataset(images, sample_limit: int):
    selected = images[:sample_limit]

    def generator():
        for image in selected:
            yield [image.astype("float32")[None, ...]]

    return generator


def load_float_manifest(path: Path) -> list[dict]:
    import json

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Quantize the generated image classification Keras models to int8 TFLite.",
    )
    parser.add_argument("--config", help="Optional path to the phase 1 JSON config")
    parser.add_argument(
        "--float-manifest",
        help="Optional path to the float model manifest. Defaults to <artifact_root>/float_models/manifest.json",
    )
    parser.add_argument(
        "--dataset-root",
        help="Optional CIFAR-10 root. Defaults to the path in the phase 1 config.",
    )
    parser.add_argument(
        "--output-root",
        help="Optional output root. Defaults to <artifact_root>/quantized_models",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Quantize only the first N entries from the float manifest",
    )
    parser.add_argument(
        "--representative-samples",
        type=int,
        help="Override the representative dataset sample count from the config",
    )
    args = parser.parse_args()

    config, _ = load_phase1_config(args.config)
    artifact_root = artifact_root_from_config(config)
    float_manifest = (
        Path(args.float_manifest).resolve()
        if args.float_manifest
        else artifact_root / "float_models" / "manifest.json"
    )
    output_root = Path(args.output_root).resolve() if args.output_root else artifact_root / "quantized_models"
    dataset_root = Path(args.dataset_root).resolve() if args.dataset_root else dataset_root_from_config(config)
    entries = load_float_manifest(float_manifest)
    if args.limit is not None:
        entries = entries[: args.limit]
    if not entries:
        raise ValueError("No float models were selected for quantization")

    import os

    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    import tensorflow as tf

    images, _, _ = load_cifar10_split(dataset_root, "train")
    sample_limit = args.representative_samples or int(config["quantization"]["representative_samples"])

    manifest_entries = []
    for entry in entries:
        model_path = Path(entry["model_path"]).resolve()
        variant_dir = ensure_directory(output_root / entry["name"])
        tflite_path = variant_dir / "model_quant.tflite"

        model = tf.keras.models.load_model(model_path, compile=False)
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.representative_dataset = representative_dataset(images, sample_limit)
        converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
        converter.inference_input_type = tf.int8
        converter.inference_output_type = tf.int8
        tflite_model = converter.convert()
        tflite_path.write_bytes(tflite_model)

        metadata = {
            "family": entry["family"],
            "name": entry["name"],
            "float_model_path": str(model_path),
            "tflite_path": str(tflite_path),
            "representative_samples": sample_limit,
            "input_type": "int8",
            "output_type": "int8",
            "params": entry["params"],
            "variant": entry["variant"],
        }
        write_json(variant_dir / "metadata.json", metadata)
        manifest_entries.append(metadata)
        print(f"Quantized {entry['name']} -> {tflite_path}")

    write_json(output_root / "manifest.json", manifest_entries)
    print(f"Manifest written to {output_root / 'manifest.json'}")


if __name__ == "__main__":
    main()
