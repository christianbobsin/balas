import argparse
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
from python_scripts.code_generator.generator import generate_cpp_code
from python_scripts.deployer.deployer import compile_cpp_project, deploy_to_mcu
from python_scripts.arena_estimator.estimator import estimate_tensor_arena_size
from python_scripts.profiler.profiler import send_random_input_and_get_result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model_quant", help="Path to the quantized model file")
    #parser.add_argument("f32_test_dataset", help="Path to the float32 test dataset file")
    #parser.add_argument("serial_device", help="Path to the serial device (e.g. /dev/ttyUSB0)")
    args = parser.parse_args()

    print("Estimating tensor arena size")
    estimated_arena_size = estimate_tensor_arena_size(args.model_quant)
    print(f"Estimated arena size: {estimated_arena_size}\n")
    print("Generating C++ code")
    generate_cpp_code(args.model_quant, estimated_arena_size)
    print("Generating C++ code done\n")
    print("Compiling C++ project")
    compile_cpp_project()
    print("Compiling C++ project done\n")
    print("Deploying to MCU")
    deploy_to_mcu()
    print("Deploy done\n")
    print("Sending random test input data")
    inference_time_us = send_random_input_and_get_result(args.model_quant, "/dev/ttyACM0")
    print(f"Inference Time with random data: {inference_time_us} us\n")