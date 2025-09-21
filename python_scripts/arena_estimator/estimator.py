import subprocess

def estimate_tensor_arena_size(model_path: str) -> int:
    """Runs stm32tflm with a quantized TFLite model and returns the RAM usage in bytes."""
    result = subprocess.run(
        ["/home/bruno/X-Cube-AI/Utilities/linux/stm32tflm", model_path],
        capture_output=True,
        text=True,
        check=True
    )
    
    for line in result.stdout.splitlines():
        if line.startswith("Ram:"):
            return int(line.split(":")[1].strip())
    
    raise RuntimeError("RAM usage not found in output")
