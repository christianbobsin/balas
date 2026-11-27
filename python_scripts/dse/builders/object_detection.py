import os
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

from python_scripts.dse.builders._graph import quantize_to_tflite


# Builder de detecção de objetos e faces (od01) — TinyissimoYOLO.
#
# Origem: item E6 da proposta de extensão do MLPerf Tiny (mapeamento sistemático
# de TinyML), estudo S115. Dataset de referência: WIDER FACE (1 classe, B = 2).
#
# Topologia de referência:
#   - Entrada: (88, 88, 3), imagem RGB 88x88 como no paper do TinyissimoYOLO
#   - Conv 3x3 16 -> MaxPool -> Conv 16 -> Conv 16 -> MaxPool -> Conv 32 -> Conv 32
#     -> MaxPool -> Conv 64 -> Conv 64 -> MaxPool -> Conv 64 -> Conv 128 -> MaxPool
#     -> Conv 128 -> Flatten (2x2x128 = 512) -> Dense 256 ReLU -> Dense 176 linear
#   - Cada Conv é 3x3 'same' seguida de BN e ReLU; MaxPool 2x2 com stride 2
#   - Saída: 176 = grade 4x4 x (2 caixas x 5 valores + 1 classe)
#
# Origem da topologia e desvios:
#   - A sequência de convoluções é a do tinyissimo-v1-small.yaml do repositório
#     oficial (ETH-PBL/TinyissimoYOLO), que segue a progressão de 16 a 128 canais
#     do paper. A cabeça (Dense 256 e saída 4x4x(B*5+C)) é a do paper.
#   - ReLU, como na implantação do paper no MAX78000.
#   - O resultado tem ~509 mil parâmetros, contra 422 mil no paper, porque a
#     lista exata de camadas da versão original não foi publicada.
#   - NMS (supressão de caixas sobrepostas) não faz parte do modelo.
#   - Pesos aleatórios determinísticos (sem treino); serve para medir custo, não acurácia.
#
# Limitação conhecida (fase 1): não cabe em nenhuma das três placas com as
# configurações atuais (heap de 32 KB da NXP, 128 KB de DTCM da STM32, RAM da
# Nordic). Versões menores ficam para a fase 2.
#
# Fase 1: modelo único (referência). A chave 'variant' existe só para o TOML ter
# um grid válido e o nome do arquivo .tflite ser legível.
GRID_KEYS = ("variant",)
DEFAULT_INPUT_SHAPE = (88, 88, 3)
DEFAULT_NUM_CLASSES = 4 * 4 * (2 * 5 + 1)  # 176
_SEED = 72


def _check_specs(input_shape, num_classes):
    """Fase 1 só tem a referência: recusa formas diferentes em vez de ignorá-las."""
    if input_shape is not None and tuple(int(d) for d in input_shape) != DEFAULT_INPUT_SHAPE:
        raise ValueError(f"od01 (fase 1) só aceita input_shape {DEFAULT_INPUT_SHAPE}; recebido {tuple(input_shape)}.")
    if num_classes is not None and int(num_classes) != DEFAULT_NUM_CLASSES:
        raise ValueError(f"od01 (fase 1) só aceita num_classes {DEFAULT_NUM_CLASSES}; recebido {num_classes}.")


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
    layout = [16, "P", 16, 16, "P", 32, 32, "P", 64, 64, "P", 64, 128, "P", 128]
    conv_i = pool_i = 0
    for step in layout:
        if step == "P":
            pool_i += 1
            x = L.MaxPooling2D((2, 2), name=f"maxpool_{pool_i}")(x)
        else:
            conv_i += 1
            x = L.Conv2D(step, 3, padding="same", name=f"conv_{conv_i}", **b)(x)
            x = L.BatchNormalization(name=f"bn_{conv_i}")(x)
            x = L.Activation("relu", name=f"relu_{conv_i}")(x)
    x = L.Flatten(name="flatten")(x)  # 2 x 2 x 128 = 512
    x = L.Dense(256, activation="relu", name="fc", **b)(x)
    outputs = L.Dense(DEFAULT_NUM_CLASSES, name="detections", **b)(x)
    return tf.keras.Model(inputs, outputs, name="od01")


def build_and_quantize_model(
    config: dict,
    variant_name: str,
    tmp_dir: Path,
    input_shape=DEFAULT_INPUT_SHAPE,
    num_classes=DEFAULT_NUM_CLASSES,
) -> Path:
    model = build_keras_model(config, input_shape, num_classes)
    return quantize_to_tflite(model, variant_name, tmp_dir)
