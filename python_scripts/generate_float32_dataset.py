import argparse
from pathlib import Path

import numpy as np


def parse_shape(shape_text: str) -> tuple[int, ...]:
    shape = tuple(int(part.strip()) for part in shape_text.split(",") if part.strip())
    if not shape:
        raise ValueError("Shape must contain at least one dimension.")
    return shape


def infer_shape_from_model(model_path: str) -> tuple[int, ...]:
    import tensorflow as tf

    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    raw_shape = interpreter.get_input_details()[0]["shape"]
    return tuple(1 if int(dim) < 0 else int(dim) for dim in raw_shape)


def build_sample(
    rng: np.random.Generator,
    shape: tuple[int, ...],
    mode: str,
    range_min: float,
    range_max: float,
) -> np.ndarray:
    if mode == "zeros":
        return np.zeros(shape, dtype=np.float32)
    if mode == "uniform":
        return rng.uniform(range_min, range_max, size=shape).astype(np.float32)
    if mode == "uint8_as_float32":
        return rng.integers(0, 256, size=shape, dtype=np.uint8).astype(np.float32)
    raise ValueError(f"Unsupported generation mode: {mode}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a directory of float32 .bin files for profiling input tensors.",
    )
    parser.add_argument("output_dir", help="Directory where sample_XXX.bin files will be created")
    parser.add_argument(
        "--samples",
        type=int,
        default=10,
        help="Number of .bin samples to generate",
    )
    parser.add_argument(
        "--model-path",
        help="Infer the input tensor shape from a .tflite model",
    )
    parser.add_argument(
        "--shape",
        help="Explicit input shape, for example 1,32,32,3",
    )
    parser.add_argument(
        "--mode",
        choices=["zeros", "uniform", "uint8_as_float32"],
        default="uniform",
        help="How to fill each float32 tensor",
    )
    parser.add_argument(
        "--range-min",
        type=float,
        default=0.0,
        help="Minimum value for uniform generation",
    )
    parser.add_argument(
        "--range-max",
        type=float,
        default=1.0,
        help="Maximum value for uniform generation",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed for deterministic dataset generation",
    )
    args = parser.parse_args()

    if bool(args.model_path) == bool(args.shape):
        raise ValueError("Provide exactly one of --model-path or --shape.")

    shape = infer_shape_from_model(args.model_path) if args.model_path else parse_shape(args.shape)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)
    for index in range(1, args.samples + 1):
        sample = build_sample(rng, shape, args.mode, args.range_min, args.range_max)
        sample_path = output_dir / f"sample_{index:03d}.bin"
        sample.tofile(sample_path)

    bytes_per_sample = int(np.prod(shape) * np.dtype(np.float32).itemsize)
    print(f"Generated {args.samples} samples in {output_dir}")
    print(f"Input shape: {shape}")
    print(f"Mode: {args.mode}")
    print(f"Bytes per sample: {bytes_per_sample}")


if __name__ == "__main__":
    main()
