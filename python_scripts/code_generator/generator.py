import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow.lite.python import schema_py_generated as schema_fb

from python_scripts.code_generator.resolver_map import resolver_map
from python_scripts.file_utils import find_and_replace, copy_file, replace_line

NXP_MODEL_DIR = Path("cpp-project/tflite-test/model")
STM32_MODEL_DIR = Path("cpp-project/stm32-tflite-test/Core/Model")
NORDIC_MODEL_DIR = Path("cpp-project/nrf52840-tflite-test/Model")

# Custom ops sem entrada no resolver_map: nome do op -> chamada no resolver.
CUSTOM_RESOLVER_CALLS = {
    "NeutronGraph": "AddCustom(tflite::GetString_NEUTRON_GRAPH(), tflite::Register_NEUTRON_GRAPH())",
}

def analyze_model(model_file):
    interpreter = tf.lite.Interpreter(model_path=model_file)
    interpreter.allocate_tensors()
    ops_details = interpreter._get_ops_details()
    input_details = interpreter.get_input_details()[0]
    output_details = interpreter.get_output_details()[0]
    inputs = np.prod(input_details['shape'])
    outputs = np.prod(output_details['shape'])
    return inputs, outputs, ops_details

def read_model_ops(model_file):
    """Lê os ops direto do flatbuffer, sem instanciar o interpretador.

    Funciona com custom ops (ex.: NeutronGraph) que o interpretador Python
    não consegue carregar. Retorna no mesmo formato de ``_get_ops_details()``.
    """
    with open(model_file, "rb") as f:
        model = schema_fb.ModelT.InitFromObj(schema_fb.Model.GetRootAsModel(f.read(), 0))
    builtin_names = {
        value: name for name, value in vars(schema_fb.BuiltinOperator).items()
        if not name.startswith("_")
    }
    ops_details = []
    for code in model.operatorCodes:
        if code.customCode:
            ops_details.append({"op_name": code.customCode.decode()})
        else:
            builtin = max(code.builtinCode, code.deprecatedBuiltinCode)
            ops_details.append({"op_name": builtin_names[builtin]})
    return ops_details

def patch_neutron_empty_tensors(model_file):
    """Troca o shape [0] dos tensores NeutronProfile/NeutronDebug por [1].

    O TFLM upstream rejeita saídas com dimensão <= 0 ("Dynamic tensors are
    not supported") durante o AllocateTensors(); o TFLM da NXP abre exceção
    para tensores 1-D de tamanho 0, o nosso não. Com o profiling desligado o
    driver não escreve nesses tensores, então 1 byte basta. O patch é feito
    in-place nos bytes do flatbuffer para preservar o alinhamento de 16 bytes
    dos buffers NeutronWeights/NeutronMicrocode.
    """
    data = bytearray(Path(model_file).read_bytes())
    model = schema_fb.Model.GetRootAsModel(data, 0)
    patched = 0
    for s in range(model.SubgraphsLength()):
        subgraph = model.Subgraphs(s)
        for t in range(subgraph.TensorsLength()):
            tensor = subgraph.Tensors(t)
            if tensor.Name() not in (b"NeutronProfile", b"NeutronDebug"):
                continue
            # Campo 0 da tabela Tensor (vtable offset 4) é o vetor shape.
            offset = tensor._tab.Offset(4)
            if not offset or tensor._tab.VectorLen(offset) != 1:
                continue
            pos = tensor._tab.Vector(offset)
            if int.from_bytes(data[pos:pos + 4], "little", signed=True) == 0:
                data[pos:pos + 4] = (1).to_bytes(4, "little", signed=True)
                patched += 1
    if patched:
        Path(model_file).write_bytes(bytes(data))
    return patched

TENSOR_TYPE_BYTES = {
    "FLOAT32": 4, "FLOAT16": 2, "INT32": 4, "UINT32": 4, "INT64": 8,
    "INT16": 2, "UINT16": 2, "INT8": 1, "UINT8": 1, "BOOL": 1,
}

def estimate_npu_arena_size(model_file, overhead_bytes=16 * 1024):
    """Limite superior da arena para um modelo NPU (sem reuso de memória).

    O stm32tflm não analisa modelos com NeutronGraph, então soma os tensores
    não-constantes (alinhados em 16 bytes) e adiciona uma margem para as
    estruturas do TFLM e o contexto do driver Neutron.
    """
    model = schema_fb.ModelT.InitFromObj(
        schema_fb.Model.GetRootAsModel(Path(model_file).read_bytes(), 0)
    )
    type_names = {
        value: name for name, value in vars(schema_fb.TensorType).items()
        if not name.startswith("_")
    }
    total = 0
    for subgraph in model.subgraphs:
        for tensor in subgraph.tensors:
            buffer = model.buffers[tensor.buffer] if tensor.buffer < len(model.buffers) else None
            if buffer is not None and buffer.data is not None and len(buffer.data):
                continue
            n_bytes = int(np.prod(tensor.shape)) if tensor.shape is not None else 0
            n_bytes *= TENSOR_TYPE_BYTES.get(type_names[tensor.type], 4)
            total += (n_bytes + 15) // 16 * 16
    return (total + overhead_bytes + 1023) // 1024 * 1024

def get_resolver_function_names(ops_details):
    function_names = []
    for op in ops_details:
        name = op['op_name']
        if name in CUSTOM_RESOLVER_CALLS:
            call = CUSTOM_RESOLVER_CALLS[name]
        elif name in resolver_map:
            call = f"{resolver_map[name]}()"
        else:
            continue
        if call not in function_names:
            function_names.append(call)
    return function_names

def get_resolver_function_calls_code(ops_details):
    function_names = get_resolver_function_names(ops_details)
    resolver_code = ""
    for name in function_names:
        resolver_code += f"\tresolver.{name};\n"
    return (len(function_names), resolver_code)

def replace_define(file_path, name, value):
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")
    pattern = re.compile(rf"^#define\s+{re.escape(name)}\s+.+$", re.MULTILINE)
    updated, count = pattern.subn(f"#define {name} {value}", content, count=1)
    if count:
        path.write_text(updated, encoding="utf-8")


def replace_generated_block(file_path, begin_marker, end_marker, replacement):
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"(// {re.escape(begin_marker)}\n)(.*?)(\n\s*// {re.escape(end_marker)})",
        re.DOTALL,
    )
    updated, count = pattern.subn(rf"\1{replacement}\3", content, count=1)
    if count:
        path.write_text(updated, encoding="utf-8")


def generate_resolver_code(ops_details, model_dir=NXP_MODEL_DIR):
    n_ops, resolver_code = get_resolver_function_calls_code(ops_details)
    model_dir = Path(model_dir)
    model_h = model_dir / "model.h"
    model_cpp = model_dir / "model.cpp"
    find_and_replace(str(model_h), "GEN_N_OPS", str(n_ops))
    replace_define(model_h, "N_OPS", str(n_ops))
    find_and_replace(str(model_cpp), "GEN_RESOLVER_OPS", resolver_code)
    replace_generated_block(
        model_cpp,
        "BALAS_GENERATED_RESOLVER_OPS_BEGIN",
        "BALAS_GENERATED_RESOLVER_OPS_END",
        resolver_code.rstrip(),
    )

def generate_tensor_arena_code(tensor_arena_size, model_dir=NXP_MODEL_DIR):
    model_h = Path(model_dir) / "model.h"
    find_and_replace(str(model_h), "GEN_TENSOR_ARENA_SIZE", str(tensor_arena_size))
    replace_define(model_h, "TENSOR_ARENA_SIZE", str(tensor_arena_size))

def generate_io_code(inputs, outputs):
    find_and_replace("cpp-project/tflite-test/model/input.h", "GEN_INPUT_SIZE", str(inputs))
    find_and_replace("cpp-project/tflite-test/model/output.h", "GEN_OUTPUT_SIZE", str(outputs))

def generate_model_binary(model_file, model_dir=NXP_MODEL_DIR):
    model_data_path = Path(model_dir) / "model_data.h"
    try:
        with model_data_path.open("w", encoding="utf-8") as output:
            subprocess.run(["xxd", "-i", model_file], stdout=output, check=True)
    except subprocess.CalledProcessError as e:
        print(f"XDD Command failed with return code {e.returncode}")
        exit()
    updated_binary_header = """
#pragma once
alignas(16) const unsigned char model_data[] = {
"""
    replace_line(str(model_data_path), 1, updated_binary_header)
    with open(model_data_path, "r", encoding="utf-8") as file:
        content = file.read()
    normalized_content = re.sub(
        r"unsigned int [A-Za-z0-9_]+_len = (\d+);",
        r"unsigned int model_data_len = \1;",
        content,
    )
    with open(model_data_path, "w", encoding="utf-8") as file:
        file.write(normalized_content)


def generate_cpp_code(model_file, tensor_arena_size, model_dir=NXP_MODEL_DIR, copy_templates=True):
    model_dir = Path(model_dir)
    if copy_templates:
        copy_file("templates/model.h", str(model_dir))
        copy_file("templates/model.cpp", str(model_dir))
    generate_tensor_arena_code(tensor_arena_size, model_dir)
    inputs, outputs, ops_details = analyze_model(model_file)
    generate_resolver_code(ops_details, model_dir)
    generate_model_binary(model_file, model_dir)


def generate_npu_cpp_code(
    cpu_model_file,
    npu_model_file,
    tensor_arena_size,
    model_dir=NXP_MODEL_DIR,
    copy_templates=True,
):
    """Gera o código C++ para um modelo compilado para a NPU Neutron.

    O modelo NPU contém o custom op ``NeutronGraph`` que é desconhecido pelo
    interpretador TFLite Python, portanto não pode ser passado para
    ``analyze_model()``.  Os ops são lidos direto do flatbuffer do modelo
    NPU, já que o neutron-compiler substitui os ops offloadados por
    ``NeutronGraph`` e pode inserir outros (ex.: PAD).

    A arena estimada para o modelo CPU pode não caber o NeutronScratch, então
    usa o maior valor entre ela e ``estimate_npu_arena_size()``. Retorna o
    tamanho de arena efetivamente usado.
    """
    model_dir = Path(model_dir)
    if copy_templates:
        copy_file("templates/model.h", str(model_dir))
        copy_file("templates/model.cpp", str(model_dir))
    patch_neutron_empty_tensors(npu_model_file)
    tensor_arena_size = max(tensor_arena_size, estimate_npu_arena_size(npu_model_file))
    generate_tensor_arena_code(tensor_arena_size, model_dir)
    ops_details = read_model_ops(npu_model_file)
    generate_resolver_code(ops_details, model_dir)
    # Serializa o binário do modelo NPU (model_data.h).
    generate_model_binary(npu_model_file, model_dir)
    return tensor_arena_size


def generate_stm32_tflm_code(model_file, tensor_arena_size):
    generate_cpp_code(
        model_file,
        tensor_arena_size,
        model_dir=STM32_MODEL_DIR,
        copy_templates=False,
    )


def generate_nordic_tflm_code(model_file, tensor_arena_size):
    generate_cpp_code(
        model_file,
        tensor_arena_size,
        model_dir=NORDIC_MODEL_DIR,
        copy_templates=False,
    )
