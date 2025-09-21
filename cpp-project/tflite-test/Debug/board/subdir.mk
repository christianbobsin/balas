################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../board/board.c \
../board/clock_config.c \
../board/peripherals.c \
../board/pin_mux.c 

C_DEPS += \
./board/board.d \
./board/clock_config.d \
./board/peripherals.d \
./board/pin_mux.d 

OBJS += \
./board/board.o \
./board/clock_config.o \
./board/peripherals.o \
./board/pin_mux.o 


# Each subdirectory must supply rules for building sources it contributes
board/%.o: ../board/%.c board/subdir.mk
	@echo 'Building file: $<'
	@echo 'Invoking: MCU C Compiler'
	arm-none-eabi-gcc -D__NEWLIB__ -DCPU_MCXN947VDF -DCPU_MCXN947VDF_cm33 -DCPU_MCXN947VDF_cm33_core0 -DSERIAL_PORT_TYPE_UART=1 -DSDK_DEBUGCONSOLE=1 -D__MCUXPRESSO -D__USE_CMSIS -DDEBUG -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/drivers" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/device" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/utilities/debug_console" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/component/uart" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/utilities/debug_console/config" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/component/serial_manager" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/component/lists" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/device/periph" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/utilities" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/CMSIS" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/CMSIS/m-profile" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/utilities/str" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/board" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/source" -O0 -fno-common -g3 -gdwarf-4 -Wall -c -ffunction-sections -fdata-sections -fno-builtin -fmerge-constants -fmacro-prefix-map="$(<D)/"= -mcpu=cortex-m33 -mfpu=fpv5-sp-d16 -mfloat-abi=hard -mthumb -D__NEWLIB__ -fstack-usage -specs=nano.specs -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.o)" -MT"$(@:%.o=%.d)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


clean: clean-board

clean-board:
	-$(RM) ./board/board.d ./board/board.o ./board/clock_config.d ./board/clock_config.o ./board/peripherals.d ./board/peripherals.o ./board/pin_mux.d ./board/pin_mux.o

.PHONY: clean-board

