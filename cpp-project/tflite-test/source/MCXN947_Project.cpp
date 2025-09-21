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
	   serial_write((uint8_t*)&inference_time_us, sizeof(int));
//	   serial_write((uint8_t*)&arena_size, sizeof(int));
	}


	return 0 ;
}
