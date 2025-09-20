import tensorflow as tf
from python_scripts.code_generator.resolver_map import resolver_map
import sys
import subprocess
from python_scripts.file_utils import find_and_replace, copy_file, replace_line

def get_ops_details(model_file):
    interpreter = tf.lite.Interpreter(model_path=model_file)
    interpreter.allocate_tensors()
    ops_details = interpreter._get_ops_details()
    return ops_details

def get_resolver_function_names(ops_details):
    function_names = []
    for op in ops_details:
        if op['op_name'] not in resolver_map.keys():
            continue
        if resolver_map[op['op_name']] not in function_names:
            function_names.append(resolver_map[op['op_name']])
    return function_names

def get_resolver_function_calls_code(model_file):
    ops_details = get_ops_details(model_file)
    function_names = get_resolver_function_names(ops_details)
    resolver_code = ""
    for name in function_names:
        resolver_code += f"\tresolver.{name}();\n"
    return (len(function_names), resolver_code)

def generate_resolver_code(model_file):
    n_ops, resolver_code = get_resolver_function_calls_code(model_file)
    find_and_replace("cpp-project/tflite-test/model/model.h", "GEN_N_OPS", str(n_ops))
    find_and_replace("cpp-project/tflite-test/model/model.cpp", "GEN_RESOLVER_OPS", resolver_code)

def generate_tensor_arena_code(tensor_arena_size):
    find_and_replace("cpp-project/tflite-test/model/model.h", "GEN_TENSOR_ARENA_SIZE", str(tensor_arena_size))

def generate_model_binary(model_file):
    command = f"xxd -i {model_file} > cpp-project/tflite-test/model/model_data.h"
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"XDD Command failed with return code {e.returncode}")
        exit()
    updated_binary_header = """
#pragma once
alignas(16) const unsigned char model_data[] = {
"""
    replace_line("cpp-project/tflite-test/model/model_data.h", 1, updated_binary_header)


def generate_cpp_code(model_file, tensor_arena_size):
    copy_file("templates/model.h", "cpp-project/tflite-test/model")
    copy_file("templates/model.cpp", "cpp-project/tflite-test/model")
    generate_tensor_arena_code(tensor_arena_size)
    generate_resolver_code(model_file)
    generate_model_binary(model_file)
