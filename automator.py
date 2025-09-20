import argparse
from python_scripts.code_generator import generate_cpp_code

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model_quant", help="Path to the quantized model file")
    parser.add_argument("f32_test_dataset", help="Path to the float32 test dataset file")
    parser.add_argument("serial_device", help="Path to the serial device (e.g. /dev/ttyUSB0)")
    args = parser.parse_args()

    generate_cpp_code(args.model_quant, 100000)