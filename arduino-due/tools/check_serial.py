#!/usr/bin/env python3
"""Verifica o eco e o heartbeat do exemplo due_serial_check (requer pyserial)."""

import argparse
import time
import uuid

import serial


def receive_for(port, seconds):
    data = bytearray()
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        data.extend(port.read(256))
    return bytes(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", default="/dev/ttyACM0")
    args = parser.parse_args()

    with serial.Serial(args.port, 115200, timeout=0.2) as port:
        print(f"Porta: {port.port}; baud: {port.baudrate}")
        # A abertura pode reiniciar o SAM3X. Espere antes de enviar os comandos.
        startup = receive_for(port, 2.5)
        port.reset_input_buffer()
        received = bytearray()
        for index in range(3):
            token = f"PING_DUE_{index}_{uuid.uuid4().hex[:12]}\n".encode("ascii")
            port.write(token)
            port.flush()
            print(f"TX: {token.decode().strip()}")
            response = bytearray()
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline and token not in response:
                response.extend(port.read(256))
            print(f"RX: {bytes(response)!r}")
            if token not in response:
                raise RuntimeError("Eco completo não recebido em 3 segundos")
            received.extend(response)
        received.extend(receive_for(port, 2.5))
        if b"DUE_OK millis=" not in startup + bytes(received):
            raise RuntimeError("Heartbeat do firmware não recebido")

    print("PASS: 3/3 ecos e heartbeat recebidos do Arduino Due")


if __name__ == "__main__":
    try:
        main()
    except (serial.SerialException, RuntimeError) as error:
        raise SystemExit(f"FALHA: {error}") from error
