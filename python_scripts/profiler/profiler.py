import struct
import argparse
import os
import time
import numpy as np
import serial

from python_scripts.config import default_serial_port

DEFAULT_SERIAL_TIMEOUT_SEC = float(os.environ.get("BALAS_SERIAL_TIMEOUT_SEC", "60"))
DEFAULT_SERIAL_MAX_RETRIES = int(os.environ.get("BALAS_SERIAL_MAX_RETRIES", "3"))

# Framed reply sent by the NXP firmware: SYNC + int32 (little-endian) + XOR checksum
FRAME_SYNC = b"\xA5\x5A"
FRAME_PAYLOAD_LEN = 5
# Time to wait after an unframed reply to detect trailing (misaligned) bytes
TRAILING_BYTES_WAIT_SEC = 0.02


class InvalidReplyError(RuntimeError):
    """The device reply was misaligned, corrupted or implausible."""


def target_uses_framing(target: str | None = None) -> bool:
    target = target or os.environ.get("BALAS_TARGET", "nxp")
    return target == "nxp"


def parse_framed_reply(payload: bytes) -> int:
    """
    Decodes the 5 bytes that follow FRAME_SYNC: int32 (little-endian) + XOR checksum.
    """
    value_bytes, checksum = payload[:4], payload[4]
    expected = value_bytes[0] ^ value_bytes[1] ^ value_bytes[2] ^ value_bytes[3]
    if checksum != expected:
        raise InvalidReplyError(
            f"Checksum mismatch in reply {payload.hex()} (expected {expected:#04x})"
        )
    return int.from_bytes(value_bytes, byteorder='little', signed=True)


class SerialLink:
    """
    Keeps one serial connection open for a batch of inferences.

    Each measurement discards stale input, sends the sample and reads the int32
    reply. On the NXP target the reply is framed (FRAME_SYNC + int32 + checksum),
    so stray bytes are skipped and corrupted replies are detected. On the other
    targets the bare int32 is read and checked for trailing bytes. Invalid replies
    are re-measured up to `max_retries` times.
    """

    def __init__(
        self,
        port_name: str,
        timeout: float = DEFAULT_SERIAL_TIMEOUT_SEC,
        max_retries: int = DEFAULT_SERIAL_MAX_RETRIES,
        framed: bool | None = None,
    ):
        self.port_name = port_name
        self.timeout = timeout
        self.max_retries = max_retries
        self.framed = target_uses_framing() if framed is None else framed
        self.ser = None

    def __enter__(self):
        self.ser = serial.Serial(
            port=self.port_name,
            baudrate=115200,
            timeout=self.timeout,
            rtscts=os.environ.get("BALAS_TARGET") == "nordic",
        )
        configure_nordic_vcom(self.ser)
        return self

    def __exit__(self, exc_type, exc, tb):
        self.ser.close()
        self.ser = None

    def measure(self, payload: bytes) -> int:
        """Sends one input payload and returns the validated int32 reply."""
        for attempt in range(self.max_retries + 1):
            self.ser.reset_input_buffer()
            self.ser.write(payload)
            self.ser.flush()
            try:
                value = self._read_framed() if self.framed else self._read_unframed()
                self._check_plausible(value)
                return value
            except InvalidReplyError as e:
                print(f"⚠️  Invalid reply (attempt {attempt + 1}/{self.max_retries + 1}): {e}")
        raise InvalidReplyError(
            f"No valid reply from {self.port_name} after {self.max_retries + 1} attempts"
        )

    def _read_exact(self, n_bytes: int) -> bytes:
        data = self.ser.read(n_bytes)
        if len(data) != n_bytes:
            raise TimeoutError(f"Did not receive {n_bytes} bytes from device")
        return data

    def _read_framed(self) -> int:
        # Scan for the sync header, skipping any stray bytes before it
        deadline = time.monotonic() + self.timeout
        window = b""
        skipped = 0
        while window != FRAME_SYNC:
            if time.monotonic() > deadline:
                raise TimeoutError("Did not receive a framed reply from device")
            byte = self.ser.read(1)
            if not byte:
                continue
            window = (window + byte)[-len(FRAME_SYNC):]
            skipped += 1
        skipped -= len(FRAME_SYNC)
        if skipped:
            print(f"⚠️  Skipped {skipped} stray byte(s) before reply header")
        return parse_framed_reply(self._read_exact(FRAME_PAYLOAD_LEN))

    def _read_unframed(self) -> int:
        resp_bytes = self._read_exact(4)
        # Extra bytes after the reply mean the 4 bytes read were not aligned
        time.sleep(TRAILING_BYTES_WAIT_SEC)
        if self.ser.in_waiting:
            extra = self.ser.read(self.ser.in_waiting)
            raise InvalidReplyError(
                f"Misaligned reply {resp_bytes.hex()} followed by {extra.hex()}"
            )
        return int.from_bytes(resp_bytes, byteorder='little', signed=True)

    def _check_plausible(self, value: int) -> None:
        if value < 0 or value > self.timeout * 1_000_000:
            raise InvalidReplyError(f"Implausible inference time {value} us")


def configure_nordic_vcom(ser: serial.Serial) -> None:
    """Assert DTR so the nRF52840-DK interface MCU drives its VCOM pins."""
    if os.environ.get("BALAS_TARGET") != "nordic":
        return
    ser.dtr = False
    time.sleep(0.1)
    ser.dtr = True
    time.sleep(0.5)
    ser.reset_input_buffer()

def load_bin_dir_as_f32_list(dir_path):
    """
    Loads all .bin files in a directory as float32 numpy arrays.

    Parameters:
        dir_path (str): Path to the directory containing .bin files.

    Returns:
        List[np.ndarray]: List of numpy arrays, each loaded from a .bin file.
    """
    arrays = []
    for fname in os.listdir(dir_path):
        if fname.endswith(".bin"):
            file_path = os.path.join(dir_path, fname)
            arr = np.fromfile(file_path, dtype=np.float32)
            arrays.append(arr)
    return arrays

def send_array_and_get_int(port_name, array: np.ndarray) -> int:
    """
    Sends a float32 numpy array via serial and reads a signed int32 response.
    Opens a new connection per call; prefer measure_arrays() for batches.

    Parameters:
        port_name (str): Serial port device name (e.g., "/dev/ttyUSB0").
        array (np.ndarray): Numpy array of dtype float32.

    Returns:
        int: The signed int32 received from the device.
    """
    return measure_arrays(port_name, [array])[0]

def measure_arrays(port_name, arrays) -> list[int]:
    """
    Sends each float32 numpy array over a single serial connection and returns
    the int32 reply (inference time in us) for each one.
    """
    for array in arrays:
        if array.dtype != np.float32:
            raise ValueError("Array must be of dtype float32")

    with SerialLink(port_name) as link:
        return [link.measure(array.tobytes()) for array in arrays]

def send_profiling_inputs(serial_port, profiling_dir):
    f32_inputs = load_bin_dir_as_f32_list(profiling_dir)
    inference_times = []
    with SerialLink(serial_port) as link:
        for count, f32_input in enumerate(f32_inputs, start=1):
            inference_time_us = link.measure(f32_input.tobytes())
            inference_times.append(inference_time_us)
            print(f"Inference {count}/{len(f32_inputs)}: {inference_time_us} us")
    return inference_times


def send_random_input_and_get_result(model_path: str, serial_port: str) -> int:
    import tensorflow as tf

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

    print(f"Sending {input_shape} float values. {len(payload)} bytes")
    with SerialLink(serial_port) as link:
        return link.measure(payload)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model_quant", help="Path to the quantized model file")
    parser.add_argument("profiling_dataset", help="Path to the dataset with .bin float32 inputs")
    parser.add_argument(
        "--serial-device",
        default=default_serial_port(),
        help="Path to the serial device (default: BALAS_SERIAL_PORT or /dev/ttyACM0)",
    )
    args = parser.parse_args()
    inference_time_us = send_random_input_and_get_result(args.model_quant, args.serial_device)
    print(f"Inference Time with random data: {inference_time_us} us")
