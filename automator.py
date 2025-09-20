import argparse
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
from python_scripts.code_generator.generator import generate_cpp_code
from python_scripts.deployer.deployer import compile_cpp_project, deploy_to_mcu

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model_quant", help="Path to the quantized model file")
    #parser.add_argument("f32_test_dataset", help="Path to the float32 test dataset file")
    #parser.add_argument("serial_device", help="Path to the serial device (e.g. /dev/ttyUSB0)")
    args = parser.parse_args()

    print("Generating C++ code")
    generate_cpp_code(args.model_quant, 110000)
    print("Compiling C++ project")
    compile_cpp_project()
    print("Deploying to MCU")
    deploy_to_mcu()
    print("Deploy done")