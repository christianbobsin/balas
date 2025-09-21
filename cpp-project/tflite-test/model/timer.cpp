#include "timer.h"
#include "peripherals.h"

void start_timing() {
	CTIMER_StartTimer(CTIMER0_PERIPHERAL);
}

int stop_timing() {
   CTIMER_StopTimer(CTIMER0_PERIPHERAL);
   uint32_t timer_val = CTIMER_GetTimerCountValue(CTIMER0_PERIPHERAL);
   CTIMER_Reset(CTIMER0_PERIPHERAL);
   return (int) timer_val;
}
