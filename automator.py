import argparse
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
from python_scripts.code_generator.generator import generate_cpp_code
from python_scripts.deployer.deployer import compile_cpp_project, deploy_to_mcu
from python_scripts.arena_estimator.estimator import estimate_tensor_arena_size
from python_scripts.profiler.profiler import send_profiling_inputs
from python_scripts.mac_calculator.mac_calculator import count_macs
from python_scripts.report_writer.report import append_inference_report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model_quant", help="Path to the quantized model file")
    parser.add_argument("profiling_dataset", help="Path to the dataset with .bin float32 inputs")
    parser.add_argument("report_file", help="Path to the csv file to append results")
    #parser.add_argument("serial_device", help="Path to the serial device (e.g. /dev/ttyUSB0)")
    args = parser.parse_args()

    print("Estimating tensor arena size")
    estimated_arena_size = estimate_tensor_arena_size(args.model_quant)
    print(f"Estimated arena size: {estimated_arena_size}\n")
    print("Calculating MACs")
    macs = count_macs(args.model_quant)
    print(f"Number of MACs: {macs}")
    print("Generating C++ code")
    generate_cpp_code(args.model_quant, estimated_arena_size)
    print("Generating C++ code done\n")
    print("Compiling C++ project")
    compile_cpp_project()
    print("Compiling C++ project done\n")
    print("Deploying to MCU")
    deploy_to_mcu()
    print("Deploy done\n")
    print("Sending profiling input data")
    inference_times = send_profiling_inputs("/dev/ttyACM0", args.profiling_dataset)
    append_inference_report(estimated_arena_size, macs, inference_times, args.report_file)
    print(f"Results saved to {args.report_file}")
