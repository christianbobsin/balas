import argparse
import os
import subprocess
from pathlib import Path
import sys
import time
import numpy as np

# REPO_ROOT aponta para a raiz do repositório (balas/)
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Imports dos utilitários do BALAS
from python_scripts.arena_estimator.estimator import estimate_tensor_arena_size
from python_scripts.config import find_neutron_compiler, repo_root
from python_scripts.mac_calculator.mac_calculator import count_macs
from python_scripts.profiler.profiler import measure_arrays

# Imports do pacote modular DSE
from python_scripts.dse.builders import get_builder_module
from python_scripts.dse.checkpoint import CheckpointManager
from python_scripts.dse.config_loader import load_dse_config
from python_scripts.dse.hashing import sample_hyperparameters_for_seed
from python_scripts.dse.hardware import HardwareAdapter

def main():
    parser = argparse.ArgumentParser(
        description="Loop de teste contínuo em TinyML (Agnóstico a Hardware e Benchmark)"
    )
    parser.add_argument(
        "--config-toml",
        default="configs/cifar_10.toml",
        help="Caminho do arquivo TOML de configuração",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Placa alvo (nxp, stm32, nordic). Se omitido, usa BALAS_TARGET.",
    )
    parser.add_argument(
        "--benchmark",
        default=None,
        help="Nome do benchmark (cifar_ten, visual_wake_words, keyword_spotting, anomaly_detection).",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Número máximo de iterações para esta execução.",
    )
    parser.add_argument(
        "--serial-device",
        default=None,
        help="Porta serial do microcontrolador (ex: /dev/ttyACM2). Se omitido, usa a porta do ambiente.",
    )
    parser.add_argument(
        "--profiling-samples",
        type=int,
        default=None,
        help="Quantidade de amostras para testar na serial por modelo.",
    )
    parser.add_argument(
        "--compare-npu",
        action="store_true",
        default=False,
        help=(
            "Quando habilitado, compila o mesmo modelo .tflite para a NPU via neutron-compiler "
            "e executa um segundo ciclo de profiling (deploy NPU) na mesma placa. "
            "Os resultados são gravados nas colunas npu_* da mesma linha do CSV. "
            "Aplicado apenas ao target NXP (MCXN94x). Padrão: False."
        ),
    )
    args = parser.parse_args()

    # 1. Ajusta variável de ambiente para o hardware target, se especificada
    if args.target:
        os.environ["BALAS_TARGET"] = args.target

    # 2. Instancia o adaptador de hardware
    hardware = HardwareAdapter(target=args.target)

    # --compare-npu só é suportado para o target NXP (MCXN94x com NPU Neutron)
    if args.compare_npu and hardware.target != "nxp":
        print(
            f"⚠️  Aviso: --compare-npu requer target 'nxp', mas o target resolvido é '{hardware.target}'. "
            "Encerrando."
        )
        sys.exit(1)

    # 3. Carrega as configurações do TOML (com precedência para --serial-device da CLI)
    dse_cfg = load_dse_config(args.config_toml, serial_override=args.serial_device)

    # 4. Sobrescreve quantidade de amostras de profiling via CLI, se informado
    if args.profiling_samples:
        dse_cfg["profiling_samples"] = args.profiling_samples

    # 5. Resolve o gerador de modelos (builder) dinamicamente
    benchmark_name = args.benchmark or dse_cfg.get("benchmark", "cifar_ten")
    builder_module = get_builder_module(benchmark_name)

    # 6. Prepara o gerenciador de checkpoint e banco de dados CSV/JSON
    # Quando --compare-npu está ativo, usa arquivos separados para não misturar
    # os datasets CPU-only e CPU+NPU.
    if args.compare_npu:
        base_csv = dse_cfg["output_csv"]
        base_map = dse_cfg["output_map"]
        dse_cfg["output_csv"] = base_csv.with_stem(base_csv.stem + "_npu_compare")
        dse_cfg["output_map"] = base_map.with_stem(base_map.stem + "_npu_compare")

    checkpoint = CheckpointManager(dse_cfg["output_csv"], dse_cfg["output_map"])

    tmp_dir = Path("/tmp/balas_continuous_models")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # 7. Prepara amostras de profiling em memória baseadas no input_shape exato do benchmark
    input_shape = dse_cfg["input_shape"]
    num_elements = int(np.prod(input_shape))
    samples = [
        np.random.uniform(0.0, 1.0, size=(num_elements,)).astype(np.float32)
        for _ in range(dse_cfg["profiling_samples"])
    ]

    print("🔄 Loop de Execução Contínua Inicializado.")
    print(f"🎯 Placa Alvo (Hardware Target): {hardware.target.upper()}")
    print(f"🧬 Benchmark Selecionado: {benchmark_name}")
    print(f"🔌 Porta Serial Resolvedora: {dse_cfg['serial_device']}")
    print(f"📐 Formato de Entrada (Input Shape): {input_shape} ({num_elements} floats)")
    print(f"📦 Modelos já processados no histórico: {len(checkpoint.completed_hashes)}")
    print(f"📄 Salvando resultados em: {dse_cfg['output_csv']}")
    print(f"🔑 Salvando mapeamento de hashes em: {dse_cfg['output_map']}")
    if args.compare_npu:
        print("⚡ Modo --compare-npu ATIVO: cada modelo será perfilado também na NPU.")
    print()

    iteration = 0
    try:
        while True:
            # Verifica se atingiu o limite de iterações configurado
            if args.max_iterations and iteration >= args.max_iterations:
                print(f"🏁 Alcançado limite máximo de {args.max_iterations} iterações.")
                break

            seed = dse_cfg["base_seed"] + iteration
            config, hp_list, hash_id, variant_name = sample_hyperparameters_for_seed(
                dse_cfg["grid"], seed
            )

            # --- CHECKPOINT: Se o Hash já foi testado, PULA ---
            if checkpoint.is_completed(hash_id):
                iteration += 1
                continue

            print(
                f"[{time.strftime('%H:%M:%S')}] 🚀 Modelo #{iteration+1} | Hash: {hash_id} | Variante: {variant_name}"
            )
            print(f"   Hiperparâmetros: {hp_list}")

            error_msg = ""
            estimated_arena = None
            macs = None
            durations = None
            # Variáveis para a execução NPU (preenchidas apenas com --compare-npu)
            npu_durations = None
            npu_error_msg = ""

            try:
                # PASSO A: Constrói e quantiza o modelo .tflite via builder dinâmico
                tflite_path = builder_module.build_and_quantize_model(
                    config,
                    variant_name,
                    tmp_dir,
                    input_shape=dse_cfg["input_shape"],
                    num_classes=dse_cfg.get("num_classes"),
                )

                # PASSO B: Estima Arena de RAM e calcula MACs
                estimated_arena = estimate_tensor_arena_size(str(tflite_path))
                macs = count_macs(str(tflite_path))

                # PASSO C: Atualiza C++, Compila e faz Deploy (firmware CPU)
                hardware.generate_code(str(tflite_path), estimated_arena)
                hardware.compile()
                hardware.deploy()

                # Atraso essencial de pós-deploy para a MCU reiniciar e estabilizar a LPUART
                post_deploy_delay = float(os.environ.get("BALAS_NXP_POST_DEPLOY_DELAY_SEC", "3.0"))
                time.sleep(post_deploy_delay)

                # PASSO D: Transmite amostras via UART e mede as latências individuais (CPU)
                durations = measure_arrays(dse_cfg["serial_device"], samples)

                avg_us = float(np.mean(durations))
                std_us = float(np.std(durations))
                print(
                    f"   ✅ Sucesso! Arena: {estimated_arena} B | MACs: {macs} | Média MCU: {avg_us:.1f} µs (±{std_us:.1f} µs)"
                )

                # ----------------------------------------------------------------
                # PASSO E (opcional): Compilar para NPU e medir latência na NPU
                # Ativado apenas com a flag --compare-npu
                # ----------------------------------------------------------------
                if args.compare_npu:
                    try:
                        # E.1 – Converte o .tflite para o formato aceito pela NPU Neutron
                        #        usando o neutron-compiler do eIQ Neutron SDK.
                        #        Resolucão do executável: NEUTRON_COMPILER (.balas.env)
                        #        > neutron-compiler no PATH > caminho estático do repositório.
                        neutron_compiler = find_neutron_compiler()
                        if neutron_compiler is None:
                            raise RuntimeError(
                                "neutron-compiler não encontrado. Defina NEUTRON_COMPILER em "
                                ".balas.env ou adicione-o ao PATH."
                            )
                        npu_tflite_path = tflite_path.with_name(
                            tflite_path.stem + "_npu.tflite"
                        )
                        npu_cmd = [
                            neutron_compiler,
                            "--input", str(tflite_path),
                            "--output", str(npu_tflite_path),
                            "--target", "mcxn94x",
                        ]
                        print(f"   ⚡ [NPU] Compilando com neutron-compiler...")
                        npu_result = subprocess.run(
                            npu_cmd, capture_output=True, text=True
                        )
                        if npu_result.returncode != 0:
                            raise RuntimeError(
                                f"neutron-compiler falhou (código {npu_result.returncode}): "
                                + npu_result.stderr
                            )
                        if not npu_tflite_path.exists():
                            raise RuntimeError(
                                "neutron-compiler terminou sem erro mas o modelo NPU não foi gerado."
                            )

                        # E.2 – Gera código C++ para o modelo NPU, compila e faz deploy.
                        # O resolver de ops é derivado do modelo CPU (tflite_path) porque o
                        # modelo NPU contém NeutronGraph, desconhecido pelo interpretador Python.
                        hardware.generate_npu_code(str(tflite_path), str(npu_tflite_path), estimated_arena)
                        hardware.compile()
                        hardware.deploy()

                        # Atraso de estabilização após deploy NPU.
                        # O subsistema Neutron da MCXN94x precisa de mais tempo para
                        # inicializar do que o firmware CPU-only. Configurado por
                        # BALAS_NXP_NPU_POST_DEPLOY_DELAY_SEC (padrão: 6 s).
                        npu_post_deploy_delay = float(
                            os.environ.get("BALAS_NXP_NPU_POST_DEPLOY_DELAY_SEC", "6.0")
                        )
                        time.sleep(npu_post_deploy_delay)

                        # E.3 – Mede latências de inferência na NPU
                        npu_durations = measure_arrays(dse_cfg["serial_device"], samples)

                        npu_avg_us = float(np.mean(npu_durations))
                        npu_std_us = float(np.std(npu_durations))
                        speedup = avg_us / npu_avg_us if npu_avg_us > 0 else float("inf")
                        print(
                            f"   ⚡ [NPU] Média: {npu_avg_us:.1f} µs (±{npu_std_us:.1f} µs) "
                            f"| Speedup NPU vs CPU: {speedup:.2f}×"
                        )

                    except Exception as npu_exc:
                        npu_error_msg = str(npu_exc)
                        print(f"   ⚠️ [NPU] Falha: {npu_error_msg}")

            except Exception as e:
                error_msg = str(e)
                print(f"   ⚠️ Falha no ciclo: {error_msg}")

            # PASSO F: Grava o resultado incremental no CSV e JSON
            # Inclui colunas NPU quando disponíveis (npu_durations / npu_error_msg)
            checkpoint.save_result(
                iteration=iteration,
                hash_id=hash_id,
                variant_name=variant_name,
                hp_list=hp_list,
                config=config,
                error_msg=error_msg,
                arena_estimated=estimated_arena,
                macs=macs,
                durations=durations,
                npu_durations=npu_durations,
                npu_error_msg=npu_error_msg,
            )

            iteration += 1
            print("-" * 75)

    except KeyboardInterrupt:
        print("\n\n🛑 Interrupção pelo usuário (Ctrl+C).")
        print(
            f"💾 Checkpoint gravado com segurança. Total no banco: {len(checkpoint.completed_hashes)}"
        )

if __name__ == "__main__":
    main()
