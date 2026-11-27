"""
Testes dos novos workloads (fase 1, modelos de referência): har01, ecg01,
vib01, pvf01 e od01 (PLANO_NOVOS_WORKLOADS_BALAS.md, Tarefa 6).

Confere, para cada modelo, entrada, saída, parâmetros, MACs e operadores do
.tflite gerado a partir do TOML em configs/new_workloads/, além da regressão
dos MACs dos quatro modelos MLPerf Tiny existentes.
"""

import os
import shutil
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import tensorflow as tf

from python_scripts.arena_estimator.estimator import estimate_tensor_arena_size
from python_scripts.code_generator.resolver_map import resolver_map
from python_scripts.dse import boards
from python_scripts.dse.builders import get_builder_module, validate_grid
from python_scripts.dse.config_loader import load_dse_config
from python_scripts.dse.tflite_inspect import inspect_tflite
from python_scripts.mac_calculator.mac_calculator import count_macs

NEW_CONFIGS = REPO_ROOT / "configs" / "new_workloads"

# Números de aceite da Seção 7 do plano.
EXPECTED = {
    "har01": {
        "benchmark": "human_activity",
        "input": [1, 128, 1, 9],
        "output": [1, 6],
        "params": 9926,
        "macs": 452992,
        "ops": {"CONV_2D": 3, "MAX_POOL_2D": 2, "AVERAGE_POOL_2D": 1,
                "FULLY_CONNECTED": 1, "SOFTMAX": 1},
    },
    "ecg01": {
        "benchmark": "ecg_classification",
        "input": [1, 256, 1],
        "output": [1, 5],
        "params": 4713,
        "macs": 86096,
        "ops": {"RESHAPE": 9, "FULLY_CONNECTED": 14, "TRANSPOSE": 8, "BATCH_MATMUL": 4,
                "MUL": 6, "SOFTMAX": 3, "ADD": 4, "MEAN": 1},
    },
    "vib01": {
        "benchmark": "vibration_anomaly",
        "input": [1, 512],
        "output": [1, 512],
        "params": 232968,
        "macs": 231424,
        "ops": {"FULLY_CONNECTED": 10},
    },
    "pvf01": {
        "benchmark": "pv_forecasting",
        "input": [1, 96, 4],
        "output": [1, 4],
        "params": 4941,
        "macs": 442496,
        # Só esses três: qualquer outro operador indica que a LSTM não foi fundida.
        "ops": {"UNIDIRECTIONAL_SEQUENCE_LSTM": 1, "STRIDED_SLICE": 1, "FULLY_CONNECTED": 1},
    },
    "od01": {
        "benchmark": "object_detection",
        "input": [1, 88, 88, 3],
        "output": [1, 176],
        "params": 509330,
        "macs": 29178880,
        "ops": {"CONV_2D": 10, "MAX_POOL_2D": 5, "RESHAPE": 1, "FULLY_CONNECTED": 2},
    },
}

# MACs dos quatro modelos de referência existentes (Tarefa 1): não podem mudar.
LEGACY_MACS = {
    "anomaly_detection": 264192,
    "keyword_spotting": 2656768,
    "cifar_ten": 12501632,
    "visual_wake_words": 7489664,
}


class TestNewWorkloads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = Path(tempfile.mkdtemp(prefix="balas_new_workloads_tests_"))
        cls._cache = {}
        print(f"\n📂 Diretório temporário de testes: {cls.tmp_dir}")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)
        print("🧹 Limpeza concluída do diretório temporário.")

    # -----------------------------------------------------------------------
    # Utilitários
    # -----------------------------------------------------------------------
    @staticmethod
    def _load(model_id):
        path = NEW_CONFIGS / f"{model_id}_reference.toml"
        assert path.exists(), f"Arquivo não encontrado: {path}"
        return load_dse_config(str(path), target="dryrun")

    def _build(self, model_id, suffix=""):
        cfg = self._load(model_id)
        builder = get_builder_module(cfg["benchmark"])
        # Mesma configuração que o laço do balas monta a partir do grid (1 valor por chave).
        config = {key: values[0] for key, values in cfg["grid"].items()}
        return builder.build_and_quantize_model(
            config,
            f"{model_id}_reference{suffix}",
            self.tmp_dir,
            input_shape=cfg["input_shape"],
            num_classes=cfg["num_classes"],
        )

    def _built(self, model_id):
        """Gera o .tflite uma vez por modelo e reaproveita entre os testes."""
        if model_id not in self._cache:
            self._cache[model_id] = self._build(model_id)
        return self._cache[model_id]

    # -----------------------------------------------------------------------
    # 1. Regressão dos MACs dos modelos existentes
    # -----------------------------------------------------------------------
    def test_01_legacy_macs_unchanged(self):
        for benchmark, expected in LEGACY_MACS.items():
            with self.subTest(benchmark=benchmark):
                builder = get_builder_module(benchmark)
                tflite = builder.build_and_quantize_model({}, f"{benchmark}_macs_regression", self.tmp_dir)
                self.assertEqual(count_macs(str(tflite)), expected)

    # -----------------------------------------------------------------------
    # 2. Um teste por modelo novo
    # -----------------------------------------------------------------------
    def _check_model(self, model_id):
        exp = EXPECTED[model_id]
        cfg = self._load(model_id)
        self.assertEqual(cfg["benchmark"], exp["benchmark"])
        tflite = self._built(model_id)

        interp = tf.lite.Interpreter(
            model_path=str(tflite),
            experimental_op_resolver_type=tf.lite.experimental.OpResolverType.BUILTIN_WITHOUT_DEFAULT_DELEGATES,
        )
        interp.allocate_tensors()
        in_det = interp.get_input_details()[0]
        out_det = interp.get_output_details()[0]
        self.assertEqual(in_det["shape"].tolist(), exp["input"])
        self.assertEqual(out_det["shape"].tolist(), exp["output"])
        self.assertEqual(in_det["dtype"].__name__, "int8")
        self.assertEqual(out_det["dtype"].__name__, "int8")

        info = inspect_tflite(tflite)
        self.assertEqual(info["params"], exp["params"], "parâmetros do .tflite")
        self.assertEqual(count_macs(str(tflite)), exp["macs"], "MACs")
        self.assertEqual(dict(Counter(info["ops"])), exp["ops"], f"operadores: {info['ops']}")

    def test_02_har01(self):
        self._check_model("har01")

    def test_03_ecg01(self):
        self._check_model("ecg01")

    def test_04_vib01(self):
        self._check_model("vib01")

    def test_05_pvf01(self):
        # A contagem exata de operadores é o que garante que a LSTM foi fundida.
        self._check_model("pvf01")

    def test_06_od01(self):
        self._check_model("od01")

    # -----------------------------------------------------------------------
    # 3. Grid sem avisos
    # -----------------------------------------------------------------------
    def test_07_grid_without_warnings(self):
        for model_id in EXPECTED:
            with self.subTest(model=model_id):
                cfg = self._load(model_id)
                builder = get_builder_module(cfg["benchmark"])
                self.assertEqual(validate_grid(builder, cfg["grid"]), [])

    # -----------------------------------------------------------------------
    # 4. Todos os operadores estão no resolver do gerador de código
    # -----------------------------------------------------------------------
    def test_08_ops_in_resolver(self):
        for model_id in EXPECTED:
            with self.subTest(model=model_id):
                ops = set(inspect_tflite(self._built(model_id))["ops"])
                missing = sorted(ops - set(resolver_map))
                self.assertEqual(missing, [], f"operadores fora do resolver_map: {missing}")

    # -----------------------------------------------------------------------
    # 5. Determinismo
    # -----------------------------------------------------------------------
    @staticmethod
    def _without_orphan_buffers(data: bytes) -> bytes:
        """Reempacota o .tflite apagando o conteúdo dos buffers que nenhum tensor usa."""
        import flatbuffers
        from tensorflow.lite.python import schema_py_generated as schema

        model = schema.ModelT.InitFromObj(schema.Model.GetRootAsModel(data, 0))
        used = {t.buffer for g in model.subgraphs for t in g.tensors}
        used |= {m.buffer for m in (model.metadata or [])}
        for index, buffer in enumerate(model.buffers):
            if index not in used:
                buffer.data = None
        builder = flatbuffers.Builder(0)
        builder.Finish(model.Pack(builder), file_identifier=b"TFL3")
        return bytes(builder.Output())

    def test_09_deterministic(self):
        for model_id in EXPECTED:
            with self.subTest(model=model_id):
                first = self._built(model_id).read_bytes()
                second = self._build(model_id, suffix="_again").read_bytes()
                if model_id == "pvf01":
                    # Desvio conhecido do TF 2.21: o conversor deixa no .tflite da
                    # LSTM um buffer órfão (sobra do estado inicial, que virou tensor
                    # variável) cujo conteúdo muda entre conversões no mesmo processo.
                    # Nenhum tensor o referencia; fora dele, os arquivos são idênticos.
                    self.assertEqual(
                        self._without_orphan_buffers(first),
                        self._without_orphan_buffers(second),
                        "dois builds geraram .tflite diferentes (fora dos buffers órfãos)",
                    )
                else:
                    self.assertEqual(first, second, "dois builds geraram .tflite diferentes")

    # -----------------------------------------------------------------------
    # 6. od01 não cabe em nenhuma placa (limitação conhecida da fase 1)
    # -----------------------------------------------------------------------
    def test_10_od01_does_not_fit(self):
        tflite = self._built("od01")
        info = inspect_tflite(tflite)
        arena = estimate_tensor_arena_size(str(tflite))
        for target, board in boards.BOARDS.items():
            with self.subTest(board=target):
                result = boards.fits(board, info["tflite_bytes"], arena, info["input_elements"])
                self.assertFalse(result["fits"], f"od01 deveria não caber em {target}: {result}")


if __name__ == "__main__":
    unittest.main()
