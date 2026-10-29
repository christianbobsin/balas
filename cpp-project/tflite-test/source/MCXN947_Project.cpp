#include "peripherals.h"
#include "pin_mux.h"
#include "clock_config.h"
/* TODO: insert other include files here. */
#include "model.h"
#include "input.h"
#include "output.h"
#include "serial_io.h"
#include "timer.h"
#include <exception>
#include <cstring>

// Reply frame: 0xA5 0x5A | int32 (little-endian) | XOR of the 4 value bytes.
// The sync header lets the host skip stray bytes and detect misaligned reads.
static void send_framed_int(int value) {
	uint8_t frame[7] = {0xA5, 0x5A};
	std::memcpy(&frame[2], &value, sizeof(value));
	frame[6] = frame[2] ^ frame[3] ^ frame[4] ^ frame[5];
	serial_write(frame, sizeof(frame));
}


int main(void) {
	BOARD_InitBootPins();
	BOARD_InitBootClocks();
	BOARD_InitBootPeripherals();

	MyModel model;
	ModelInput input(model.get_input_size());
	ModelOutput output(model.get_output_size()); 


	while (1) {
	   serial_read((uint8_t*)input.data, input.size);
	   start_timing();
	   model.run_inference(input, output);
	   int inference_time_us = stop_timing();
	   send_framed_int(inference_time_us);
//	   serial_write((uint8_t*)&arena_size, sizeof(int));
	}


	return 0 ;
}
