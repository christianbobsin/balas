import sys
import numpy as np
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import tensorflow as tf

def count_macs(model_path):
    # Sem o delegate XNNPACK: ele falha ao preparar alguns modelos int8 válidos
    # (ex.: MobileNetV1 com TANH) e a contagem só precisa das formas.
    interpreter = tf.lite.Interpreter(
        model_path=str(model_path),
        experimental_op_resolver_type=tf.lite.experimental.OpResolverType.BUILTIN_WITHOUT_DEFAULT_DELEGATES,
    )
    interpreter.allocate_tensors()  # Needed for shape resolution

    total_macs = 0

    for op in interpreter._get_ops_details():
        op_name = op['op_name']
        inputs = op['inputs']
        outputs = op['outputs']

        layer_macs = 0
        if inputs.size != 0 and outputs.size != 0:
            input_details = interpreter.get_tensor_details()[inputs[0]]
            output_details = interpreter.get_tensor_details()[outputs[0]]

            input_shape = input_details['shape']
            output_shape = output_details['shape']

            if op_name == 'CONV_2D':
                kernel_shape = interpreter.get_tensor_details()[inputs[1]]['shape']
                out_ch, kh, kw, in_ch = kernel_shape
                out_elems = np.prod(output_shape[1:])
                layer_macs = out_elems * kh * kw * in_ch

            elif op_name == 'DEPTHWISE_CONV_2D':
                kernel_shape = interpreter.get_tensor_details()[inputs[1]]['shape']
                x, kh, kw, in_ch = kernel_shape
                out_elems = np.prod(output_shape[1:])
                layer_macs = out_elems * kh * kw

            elif op_name == 'FULLY_CONNECTED':
                # Pesos do TFLite têm forma (saída, entrada). Cada elemento da saída
                # custa 'entrada' MACs; vale para entrada 2D (1, n) e 3D (1, tokens, n).
                weight_shape = interpreter.get_tensor_details()[inputs[1]]['shape']
                in_dim = int(weight_shape[1])
                layer_macs = int(np.prod(output_shape)) * in_dim

            elif op_name == 'BATCH_MATMUL':
                # Saída (..., M, N) = A (..., M, K) x B (..., K, N); o Keras gera adj_x = False.
                a_shape = interpreter.get_tensor_details()[inputs[0]]['shape']
                b_shape = interpreter.get_tensor_details()[inputs[1]]['shape']
                k = int(a_shape[-1])
                if k not in (int(b_shape[-1]), int(b_shape[-2])):
                    raise ValueError(f"BATCH_MATMUL com formas inesperadas: {a_shape} x {b_shape}")
                layer_macs = int(np.prod(output_shape)) * k

            elif op_name == 'UNIDIRECTIONAL_SEQUENCE_LSTM':
                # Entrada (1, passos, features). inputs[2] = pesos entrada->porta de esquecimento,
                # forma (units, features); é obrigatório (inputs[1] pode faltar em variantes CIFG).
                if len(input_shape) != 3:
                    raise ValueError(f"LSTM com entrada inesperada: {input_shape}")
                steps, features = int(input_shape[1]), int(input_shape[2])
                units = int(interpreter.get_tensor_details()[inputs[2]]['shape'][0])
                layer_macs = steps * 4 * units * (features + units)

        total_macs += layer_macs

    return total_macs

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} model.tflite")
        sys.exit(1)

    model_path = sys.argv[1]
    count_macs(model_path)
