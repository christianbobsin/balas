#!/usr/bin/env python3
import sys
import serial
import os
import struct


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <serial_port> <num_bytes>")
    sys.exit(1)

port = sys.argv[1]
num_bytes = int(sys.argv[2])

# Generate random bytes
data = os.urandom(num_bytes)

# Open serial port
ser = serial.Serial(port, baudrate=115200, timeout=5)

# Send data
ser.write(data)
print(f"Sent {num_bytes} random bytes to {port}")

# Read 4 response bytes
resp = ser.read(4)
ser.close()


if len(resp) == 4:
    val = struct.unpack("<I", resp)[0]  # little-endian unsigned int
    print("Received unsigned int:", val)
else:
    print(f"Timeout: received only {len(resp)} bytes -> {resp.hex()}")