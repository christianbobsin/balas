import subprocess
from python_scripts.config import find_stm32tflm

def estimate_tensor_arena_size(model_path: str) -> int:
    """Runs stm32tflm with a quantized TFLite model and returns the RAM usage in bytes."""
    stm32tflm_bin = find_stm32tflm()
    if not stm32tflm_bin:
        raise FileNotFoundError(
            "stm32tflm not found. Set BALAS_STM32TFLM_BIN, add stm32tflm to PATH, "
            "or install X-CUBE-AI/ST Edge AI in a standard location."
        )

    result = subprocess.run(
        [stm32tflm_bin, model_path],
        capture_output=True,
        text=True,
        check=True
    )
    
    for line in result.stdout.splitlines():
        if line.startswith("Ram:"):
            return int(line.split(":")[1].strip())
    
    raise RuntimeError("RAM usage not found in output")
