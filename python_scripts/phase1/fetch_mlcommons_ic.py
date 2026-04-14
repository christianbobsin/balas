import argparse
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python_scripts.phase1.common import load_phase1_config, mlcommons_root_from_config


REPO_URL = "https://github.com/mlcommons/tiny.git"
SPARSE_PATH = "benchmark/training/image_classification"


def run_command(args: list[str], cwd: Path | None = None) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def ensure_sparse_clone(dest: Path, ref: str) -> None:
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        run_command(["git", "clone", "--filter=blob:none", "--no-checkout", REPO_URL, str(dest)])

    if not (dest / ".git").exists():
        raise RuntimeError(f"{dest} exists but is not a git repository")

    run_command(["git", "sparse-checkout", "init", "--cone"], cwd=dest)
    run_command(["git", "sparse-checkout", "set", SPARSE_PATH], cwd=dest)
    run_command(["git", "fetch", "--depth", "1", "origin", ref], cwd=dest)
    run_command(["git", "checkout", "--detach", "FETCH_HEAD"], cwd=dest)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch the MLCommons Tiny repository with sparse checkout for image classification.",
    )
    parser.add_argument(
        "--config",
        help="Optional path to the phase 1 JSON config",
    )
    parser.add_argument(
        "--dest",
        help="Destination directory for the sparse clone. Defaults to the path in the phase 1 config.",
    )
    parser.add_argument(
        "--ref",
        default="master",
        help="Git ref to fetch from MLCommons Tiny. Default: master",
    )
    args = parser.parse_args()

    config, _ = load_phase1_config(args.config)
    dest = Path(args.dest).resolve() if args.dest else mlcommons_root_from_config(config)
    ensure_sparse_clone(dest, args.ref)

    print(f"MLCommons Tiny available at: {dest}")
    print(f"Image classification subtree: {dest / SPARSE_PATH}")


if __name__ == "__main__":
    main()
