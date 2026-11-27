import os
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

from python_scripts.dse.builders._graph import quantize_to_tflite


# Builder de classificação de batimentos de ECG (ecg01) — transformer pequeno.
#
# Origem: item E3 da proposta de extensão do MLPerf Tiny (mapeamento sistemático
# de TinyML), estudos S177 e S203. Dataset de referência: MIT-BIH Arrhythmia.
#
# Topologia de referência:
#   - Entrada: (256, 1) = um batimento de 256 amostras de uma derivação (MLII,
#     360 Hz), centrado no pico R
#   - Reshape em 16 tokens de 16 amostras -> Dense 16 por token (embedding)
#   - 2 blocos encoder, cada um:
#       MultiHeadAttention (2 cabeças, key_dim 8) -> soma residual -> BN
#       -> Dense 32 ReLU -> Dense 16 -> soma residual -> BN
#   - Média sobre os tokens (GlobalAveragePooling1D) -> Dense 5 softmax (classes AAMI)
#
# Simplificações em relação ao S177:
#   - Sem embedding posicional: é uma soma com uma constante, sem MACs.
#   - BatchNorm no lugar de LayerNorm: com LayerNorm o conversor insere trechos
#     em float (DEQUANTIZE/QUANTIZE) no meio do modelo INT8; com BatchNorm o
#     modelo inteiro fica em INT8.
#   - Pesos aleatórios determinísticos (sem treino); serve para medir custo, não acurácia.
#
# Fase 1: modelo único (referência). A chave 'variant' existe só para o TOML ter
# um grid válido e o nome do arquivo .tflite ser legível.
GRID_KEYS = ("variant",)
DEFAULT_INPUT_SHAPE = (256, 1)
DEFAULT_NUM_CLASSES = 5
_SEED = 72


def _check_specs(input_shape, num_classes):
    """Fase 1 só tem a referência: recusa formas diferentes em vez de ignorá-las."""
    if input_shape is not None and tuple(int(d) for d in input_shape) != DEFAULT_INPUT_SHAPE:
        raise ValueError(f"ecg01 (fase 1) só aceita input_shape {DEFAULT_INPUT_SHAPE}; recebido {tuple(input_shape)}.")
    if num_classes is not None and int(num_classes) != DEFAULT_NUM_CLASSES:
        raise ValueError(f"ecg01 (fase 1) só aceita num_classes {DEFAULT_NUM_CLASSES}; recebido {num_classes}.")


def build_keras_model(config: dict, input_shape=None, num_classes=None):
    """Monta o modelo de referência com pesos aleatórios. Ignora o config nesta fase."""
    _check_specs(input_shape, num_classes)
    import tensorflow as tf

    tf.keras.backend.clear_session()
    tf.keras.utils.set_random_seed(_SEED)
    L = tf.keras.layers
    b = dict(bias_initializer="random_normal")
    inputs = tf.keras.Input(DEFAULT_INPUT_SHAPE, batch_size=1, name="input")
    x = L.Reshape((16, 16), name="patchify")(inputs)  # 16 tokens x 16 amostras
    x = L.Dense(16, name="embed", **b)(x)
    for i in range(1, 3):
        att = L.MultiHeadAttention(num_heads=2, key_dim=8, name=f"mha_{i}",
                                   bias_initializer="random_normal")(x, x)
        x = L.BatchNormalization(name=f"bn_att_{i}")(L.Add(name=f"res_att_{i}")([x, att]))
        ffn = L.Dense(32, activation="relu", name=f"ffn1_{i}", **b)(x)
        ffn = L.Dense(16, name=f"ffn2_{i}", **b)(ffn)
        x = L.BatchNormalization(name=f"bn_ffn_{i}")(L.Add(name=f"res_ffn_{i}")([x, ffn]))
    x = L.GlobalAveragePooling1D(name="token_mean")(x)
    outputs = L.Dense(DEFAULT_NUM_CLASSES, activation="softmax", name="classifier", **b)(x)
    return tf.keras.Model(inputs, outputs, name="ecg01")


def build_and_quantize_model(
    config: dict,
    variant_name: str,
    tmp_dir: Path,
    input_shape=DEFAULT_INPUT_SHAPE,
    num_classes=DEFAULT_NUM_CLASSES,
) -> Path:
    model = build_keras_model(config, input_shape, num_classes)
    return quantize_to_tflite(model, variant_name, tmp_dir)
