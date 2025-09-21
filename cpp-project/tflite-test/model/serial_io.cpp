#include "serial_io.h"
#include "peripherals.h"

void serial_read(uint8_t* dst, unsigned long n_bytes) {
	LPUART_ReadBlocking(LP_FLEXCOMM4_PERIPHERAL, (uint8_t*) dst, n_bytes);
}

void serial_write(uint8_t* src, unsigned long n_bytes) {
	LPUART_WriteBlocking(LP_FLEXCOMM4_PERIPHERAL, (uint8_t*) src, n_bytes);
}
