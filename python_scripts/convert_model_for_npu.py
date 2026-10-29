import os
import shutil
import subprocess
import sys

CPU_MODEL = "model_cpu.tflite"
NPU_MODEL = "model_npu.tflite"

# Caminho do executável: variável de ambiente > PATH > caminho fixo (ajuste o seu)
NEUTRON_COMPILER = (
    os.environ.get("NEUTRON_COMPILER")
    or shutil.which("neutron-compiler")
    or r"external/eiq-neutron/neutron-compiler" 
)

cmd = [
    NEUTRON_COMPILER,
    "--input", CPU_MODEL,       
    "--output", NPU_MODEL,
    "--target", "mcxn94x",
]

print("Executando:", " ".join(cmd))
result = subprocess.run(cmd, capture_output=True, text=True)

# Guarda o log (mostra quantos ops foram para a NPU e quantos ficaram na CPU)
with open("neutron-compiler_log.txt", "w") as f:
    f.write(result.stdout + "\n" + result.stderr)

print(result.stdout)
if result.returncode != 0:
    print(result.stderr, file=sys.stderr)
    sys.exit(f"neutron-compiler falhou (código {result.returncode})")

if not os.path.exists(NPU_MODEL):
    sys.exit("O compilador terminou sem erro, mas o modelo da NPU não foi gerado.")

print(f"Modelo NPU gerado: {NPU_MODEL}")

CPU_MODEL_HEADER = "model_cpu.h"
NPU_MODEL_HEADER = "model_npu.h"

cmd_cpu = [
    "xxd", 
    "-i", CPU_MODEL,
]

cmd_npu = [
    "xxd", 
    "-i", NPU_MODEL,
]

result = subprocess.run(cmd_cpu, capture_output=True, text=True)
if result.returncode != 0:
    sys.exit(result.stderr)
with open(CPU_MODEL_HEADER, "w") as f:
    f.write(result.stdout)

result = subprocess.run(cmd_npu, capture_output=True, text=True)
if result.returncode != 0:
    sys.exit(result.stderr)
with open(NPU_MODEL_HEADER, "w") as f:
    f.write(result.stdout)    