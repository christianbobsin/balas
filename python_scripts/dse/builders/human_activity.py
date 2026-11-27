import os
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

from python_scripts.dse.builders._graph import quantize_to_tflite


# Builder de Human Activity Recognition (har01) — CNN 1D sobre sinais inerciais.
#
# Origem: item E1 da proposta de extensão do MLPerf Tiny (mapeamento sistemático
# de TinyML), estudos S29, S148, S162, S165 e S265. Dataset de referência: UCI-HAR.
#
# Topologia de referência:
#   - Entrada: (128, 1, 9) = 128 amostras (2,56 s a 50 Hz) x 9 canais inerciais brutos
#   - Conv (5x1) 16 -> BN -> ReLU -> MaxPool (2x1)
#   - Conv (5x1) 32 -> BN -> ReLU -> MaxPool (2x1)
#   - Conv (3x1) 64 -> BN -> ReLU
#   - AvgPool (32x1) -> Flatten -> Dense 6 softmax
#
# Simplificações:
#   - A convolução 1D é feita com Conv2D de kernel (k, 1) sobre entrada (T, 1, C):
#     gera CONV_2D diretamente, sem os RESHAPE/EXPAND_DIMS que o Conv1D do Keras insere.
#   - Pesos aleatórios determinísticos (sem treino); serve para medir custo, não acurácia.
#
# Fase 1: modelo único (referência). A chave 'variant' existe só para o TOML ter
# um grid válido e o nome do arquivo .tflite ser legível.
GRID_KEYS = ("variant",)
DEFAULT_INPUT_SHAPE = (128, 1, 9)
DEFAULT_NUM_CLASSES = 6
_SEED = 72


def _check_specs(input_shape, num_classes):
    """Fase 1 só tem a referência: recusa formas diferentes em vez de ignorá-las."""
    if input_shape is not None and tuple(int(d) for d in input_shape) != DEFAULT_INPUT_SHAPE:
        raise ValueError(f"har01 (fase 1) só aceita input_shape {DEFAULT_INPUT_SHAPE}; recebido {tuple(input_shape)}.")
    if num_classes is not None and int(num_classes) != DEFAULT_NUM_CLASSES:
        raise ValueError(f"har01 (fase 1) só aceita num_classes {DEFAULT_NUM_CLASSES}; recebido {num_classes}.")


def build_keras_model(config: dict, input_shape=None, num_classes=None):
    """Monta o modelo de referência com pesos aleatórios. Ignora o config nesta fase."""
    _check_specs(input_shape, num_classes)
    import tensorflow as tf

    tf.keras.backend.clear_session()
    tf.keras.utils.set_random_seed(_SEED)
    L = tf.keras.layers
    b = dict(bias_initializer="random_normal")
    inputs = tf.keras.Input(DEFAULT_INPUT_SHAPE, batch_size=1, name="input")
    x = inputs
    for i, (filters, kernel, pool) in enumerate([(16, 5, True), (32, 5, True), (64, 3, False)], 1):
        x = L.Conv2D(filters, (kernel, 1), padding="same", name=f"conv_{i}", **b)(x)
        x = L.BatchNormalization(name=f"bn_{i}")(x)
        x = L.Activation("relu", name=f"relu_{i}")(x)
        if pool:
            x = L.MaxPooling2D((2, 1), name=f"maxpool_{i}")(x)
    x = L.AveragePooling2D((32, 1), name="avgpool")(x)
    x = L.Flatten(name="flatten")(x)
    outputs = L.Dense(DEFAULT_NUM_CLASSES, activation="softmax", name="classifier", **b)(x)
    return tf.keras.Model(inputs, outputs, name="har01")


def build_and_quantize_model(
    config: dict,
    variant_name: str,
    tmp_dir: Path,
    input_shape=DEFAULT_INPUT_SHAPE,
    num_classes=DEFAULT_NUM_CLASSES,
) -> Path:
    model = build_keras_model(config, input_shape, num_classes)
    return quantize_to_tflite(model, variant_name, tmp_dir)
