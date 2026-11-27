import os
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

from python_scripts.dse.builders._graph import quantize_to_tflite


# Builder de previsão de geração fotovoltaica (pvf01) — LSTM.
#
# Origem: item E5 da proposta de extensão do MLPerf Tiny (mapeamento sistemático
# de TinyML), estudos S142, S205 e S266. Dataset de referência: State Grid,
# intervalos de 15 min.
#
# Topologia de referência:
#   - Entrada: (96, 4) = 96 passos de 15 min (24 h) x 4 variáveis
#     (potência, irradiância, temperatura, umidade)
#   - LSTM 32 (devolve só o último passo) -> Dense 4 linear
#   - Saída: 4 valores (próximos 4 passos, 1 h), regressão
#
# Por que tf_keras (Keras 2 legado):
#   - Com o Keras 3 (padrão do TF 2.21) o conversor do TFLite não reconhece a
#     LSTM e a conversão termina em segmentation fault. Com o tf_keras, no mesmo
#     TF 2.21, a LSTM vira um único operador INT8 UNIDIRECTIONAL_SEQUENCE_LSTM,
#     suportado pelo TFLM. O pacote é importado diretamente; NUNCA defina
#     TF_USE_LEGACY_KERAS, que trocaria o Keras de todos os builders.
#
# Simplificações:
#   - Pesos aleatórios determinísticos (sem treino); serve para medir custo, não acurácia.
#
# Fase 1: modelo único (referência). A chave 'variant' existe só para o TOML ter
# um grid válido e o nome do arquivo .tflite ser legível.
GRID_KEYS = ("variant",)
DEFAULT_INPUT_SHAPE = (96, 4)
DEFAULT_NUM_CLASSES = 4
_SEED = 72


def _check_specs(input_shape, num_classes):
    """Fase 1 só tem a referência: recusa formas diferentes em vez de ignorá-las."""
    if input_shape is not None and tuple(int(d) for d in input_shape) != DEFAULT_INPUT_SHAPE:
        raise ValueError(f"pvf01 (fase 1) só aceita input_shape {DEFAULT_INPUT_SHAPE}; recebido {tuple(input_shape)}.")
    if num_classes is not None and int(num_classes) != DEFAULT_NUM_CLASSES:
        raise ValueError(f"pvf01 (fase 1) só aceita num_classes {DEFAULT_NUM_CLASSES}; recebido {num_classes}.")


def build_keras_model(config: dict, input_shape=None, num_classes=None):
    """Monta o modelo de referência com pesos aleatórios. Ignora o config nesta fase."""
    _check_specs(input_shape, num_classes)
    # Keras 2 legado: com o Keras 3, o conversor do TF 2.21 não reconhece a LSTM.
    import tf_keras

    tf_keras.backend.clear_session()
    tf_keras.utils.set_random_seed(_SEED)
    L = tf_keras.layers
    inputs = tf_keras.Input(DEFAULT_INPUT_SHAPE, batch_size=1, name="input")
    x = L.LSTM(32, bias_initializer="random_normal", name="lstm")(inputs)
    outputs = L.Dense(DEFAULT_NUM_CLASSES, bias_initializer="random_normal", name="forecast")(x)
    return tf_keras.Model(inputs, outputs, name="pvf01")


def build_and_quantize_model(
    config: dict,
    variant_name: str,
    tmp_dir: Path,
    input_shape=DEFAULT_INPUT_SHAPE,
    num_classes=DEFAULT_NUM_CLASSES,
) -> Path:
    model = build_keras_model(config, input_shape, num_classes)
    return quantize_to_tflite(model, variant_name, tmp_dir)
