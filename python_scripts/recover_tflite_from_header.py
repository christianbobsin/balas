import argparse
import re
from pathlib import Path


def extract_model_bytes(header_text: str) -> tuple[bytes, int | None]:
    hex_bytes = re.findall(r"0x([0-9a-fA-F]{2})", header_text)
    if not hex_bytes:
        raise ValueError("No hex byte array was found in the header.")

    model_bytes = bytes(int(value, 16) for value in hex_bytes)
    declared_length_match = re.search(
        r"unsigned int [A-Za-z0-9_]+_len = (\d+);",
        header_text,
    )
    declared_length = None
    if declared_length_match is not None:
        declared_length = int(declared_length_match.group(1))
        if declared_length != len(model_bytes):
            raise ValueError(
                "Recovered byte count does not match the length declared in the header: "
                f"{len(model_bytes)} != {declared_length}"
            )
    return model_bytes, declared_length


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover a .tflite file from a generated C header with xxd-style hex bytes.",
    )
    parser.add_argument("header_path", help="Path to the input header, such as model_data.h")
    parser.add_argument("output_path", help="Path to the recovered .tflite output file")
    args = parser.parse_args()

    header_path = Path(args.header_path)
    output_path = Path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    model_bytes, declared_length = extract_model_bytes(
        header_path.read_text(encoding="utf-8"),
    )
    output_path.write_bytes(model_bytes)

    print(f"Recovered {len(model_bytes)} bytes from {header_path}")
    if declared_length is not None:
        print(f"Declared length check passed: {declared_length} bytes")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
