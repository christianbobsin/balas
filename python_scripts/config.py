import os
import shutil
from glob import glob
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def load_local_env() -> Path | None:
    candidates = []
    explicit = os.environ.get("BALAS_CONFIG_FILE")
    if explicit:
        candidates.append(Path(os.path.expandvars(os.path.expanduser(explicit))))
    else:
        candidates.append(REPO_ROOT / ".balas.env")
        candidates.append(REPO_ROOT / "balas.env")

    for path in candidates:
        if not path.is_file():
            continue

        with path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[7:].strip()
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = os.path.expandvars(os.path.expanduser(_strip_quotes(value)))
                os.environ.setdefault(key, value)
        return path

    return None


LOADED_CONFIG = load_local_env()


def repo_root() -> Path:
    return REPO_ROOT


def env_path(name: str) -> str | None:
    value = os.environ.get(name)
    if not value:
        return None
    return os.path.expandvars(os.path.expanduser(value))


def default_serial_port() -> str:
    return os.environ.get("BALAS_SERIAL_PORT", "/dev/ttyACM0")


def default_workspace_dir() -> Path:
    configured = env_path("MCUX_WORKSPACE_DIR") or env_path("MCUX_WORKSPACE_LOC")
    if configured:
        return Path(configured)
    return repo_root() / "cpp-project"


def default_mcuxpresso_bin() -> str:
    configured = env_path("MCUXPRESSO_IDE_BIN") or env_path("MCUXPRESSO")
    if configured:
        return configured
    return "/usr/local/mcuxpressoide/ide/mcuxpressoide"


def find_stm32tflm() -> str | None:
    configured = env_path("BALAS_STM32TFLM_BIN")
    if configured and Path(configured).is_file():
        return configured

    found = shutil.which("stm32tflm")
    if found:
        return found

    home = Path.home()
    candidate_globs = [
        str(home / "opt/st/x-cube-ai/*/stedgeai-linux-*/Utilities/linux/stm32tflm"),
        str(home / "STM32Cube/Repository/Packs/STMicroelectronics/X-CUBE-AI/*/Utilities/linux/stm32tflm"),
        str(home / "X-Cube-AI/Utilities/linux/stm32tflm"),
    ]

    for pattern in candidate_globs:
        matches = sorted(glob(pattern))
        for match in matches:
            if Path(match).is_file():
                return match

    return None
