import struct
import numpy as np
import serial
import tensorflow as tf
import argparse

def send_random_input_and_get_result(model_path: str, serial_port: str) -> int:
    # Load model
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    input_shape = input_details[0]['shape']

    # Get input size (#elements)
    input_size = np.prod(input_shape)

    # Generate random float32 data
    data = np.random.rand(input_size).astype(np.float32)

    # Serialize to bytes
    payload = struct.pack('<' + 'f' * input_size, *data)

    # Open serial
    with serial.Serial(serial_port, baudrate=115200, timeout=10) as ser:
        # Send payload
        ser.write(payload)

        # Wait for 1 integer (4 bytes, little-endian)
        resp = ser.read(4)
        if len(resp) < 4:
            raise TimeoutError("Did not receive full response from MCU")

        result = struct.unpack('<i', resp)[0]  # signed int32

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model_quant", help="Path to the quantized model file")
    #parser.add_argument("f32_test_dataset", help="Path to the float32 test dataset file")
    #parser.add_argument("serial_device", help="Path to the serial device (e.g. /dev/ttyUSB0)")
    args = parser.parse_args()
    inference_time_us = send_random_input_and_get_result(args.model_quant, "/dev/ttyACM0")
    print(f"Inference Time with random data: {inference_time_us} us")
