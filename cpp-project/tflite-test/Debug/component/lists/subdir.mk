################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../component/lists/fsl_component_generic_list.c 

C_DEPS += \
./component/lists/fsl_component_generic_list.d 

OBJS += \
./component/lists/fsl_component_generic_list.o 


# Each subdirectory must supply rules for building sources it contributes
component/lists/%.o: ../component/lists/%.c component/lists/subdir.mk
	@echo 'Building file: $<'
	@echo 'Invoking: MCU C Compiler'
	arm-none-eabi-gcc -D__NEWLIB__ -DCPU_MCXN947VDF -DCPU_MCXN947VDF_cm33 -DCPU_MCXN947VDF_cm33_core0 -DSERIAL_PORT_TYPE_UART=1 -DSDK_DEBUGCONSOLE=1 -D__MCUXPRESSO -D__USE_CMSIS -DDEBUG -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/drivers" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/device" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/utilities/debug_console" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/component/uart" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/utilities/debug_console/config" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/component/serial_manager" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/component/lists" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/device/periph" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/utilities" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/CMSIS" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/CMSIS/m-profile" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/utilities/str" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/board" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/source" -O0 -fno-common -g3 -gdwarf-4 -Wall -c -ffunction-sections -fdata-sections -fno-builtin -fmerge-constants -fmacro-prefix-map="$(<D)/"= -mcpu=cortex-m33 -mfpu=fpv5-sp-d16 -mfloat-abi=hard -mthumb -D__NEWLIB__ -fstack-usage -specs=nano.specs -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.o)" -MT"$(@:%.o=%.d)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


clean: clean-component-2f-lists

clean-component-2f-lists:
	-$(RM) ./component/lists/fsl_component_generic_list.d ./component/lists/fsl_component_generic_list.o

.PHONY: clean-component-2f-lists

