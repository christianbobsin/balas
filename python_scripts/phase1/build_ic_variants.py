import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python_scripts.phase1.common import (
    artifact_root_from_config,
    ensure_directory,
    iter_variants,
    load_phase1_config,
    select_variants,
    write_json,
)


def build_model(
    tf,
    input_shape: tuple[int, int, int],
    num_classes: int,
    variant: dict,
    pool_size: int,
    padding: str,
):
    inputs = tf.keras.Input(shape=input_shape, name="input")
    x = tf.keras.layers.Conv2D(
        variant["channels_1"],
        variant["kernel_1"],
        padding=padding,
        activation="relu",
        name="conv_1",
    )(inputs)
    x = tf.keras.layers.MaxPooling2D(pool_size=pool_size, name="pool_1")(x)
    x = tf.keras.layers.Conv2D(
        variant["channels_2"],
        variant["kernel_2"],
        padding=padding,
        activation="relu",
        name="conv_2",
    )(x)
    x = tf.keras.layers.MaxPooling2D(pool_size=pool_size, name="pool_2")(x)
    x = tf.keras.layers.Conv2D(
        variant["channels_3"],
        variant["kernel_3"],
        padding=padding,
        activation="relu",
        name="conv_3",
    )(x)
    x = tf.keras.layers.Flatten(name="flatten")(x)
    outputs = tf.keras.layers.Dense(num_classes, name="logits")(x)
    return tf.keras.Model(inputs=inputs, outputs=outputs, name=variant["name"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the image classification model variants described by the phase 1 config.",
    )
    parser.add_argument("--config", help="Optional path to the phase 1 JSON config")
    parser.add_argument(
        "--output-root",
        help="Optional output root. Defaults to <artifact_root>/float_models",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Build only the first N variants",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        help="Build only the named variants",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=1234,
        help="Base seed for deterministic random initialization",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the selected variants without writing files",
    )
    args = parser.parse_args()

    config, config_path = load_phase1_config(args.config)
    variants = select_variants(iter_variants(config), args.limit, set(args.only or []))
    if not variants:
        raise ValueError("No variants were selected")

    if args.dry_run:
        print(f"Config: {config_path}")
        print(f"Selected variants: {len(variants)}")
        for variant in variants:
            print(variant["name"])
        return

    import os

    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    import tensorflow as tf

    artifact_root = artifact_root_from_config(config)
    output_root = Path(args.output_root).resolve() if args.output_root else artifact_root / "float_models"
    ensure_directory(output_root)

    model_cfg = config["model"]
    input_shape = tuple(model_cfg["input_shape"])
    num_classes = int(model_cfg["num_classes"])
    pool_size = int(model_cfg.get("pool_size", 2))
    padding = model_cfg.get("padding", "same")

    manifest_entries = []
    for index, variant in enumerate(variants):
        tf.keras.backend.clear_session()
        tf.keras.utils.set_random_seed(args.seed + index)
        model = build_model(tf, input_shape, num_classes, variant, pool_size, padding)

        variant_dir = ensure_directory(output_root / variant["name"])
        model_path = variant_dir / "model.keras"
        model.save(model_path, overwrite=True)

        metadata = {
            "family": config["family"],
            "name": variant["name"],
            "source_config": str(config_path),
            "model_path": str(model_path),
            "params": int(model.count_params()),
            "input_shape": list(input_shape),
            "num_classes": num_classes,
            "variant": variant,
        }
        write_json(variant_dir / "metadata.json", metadata)
        manifest_entries.append(metadata)
        print(f"Built {variant['name']} -> {model_path}")

    write_json(output_root / "manifest.json", manifest_entries)
    print(f"Manifest written to {output_root / 'manifest.json'}")


if __name__ == "__main__":
    main()
