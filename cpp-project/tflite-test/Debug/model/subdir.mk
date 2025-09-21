################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
CPP_SRCS += \
../model/model.cpp \
../model/quantization.cpp \
../model/serial_io.cpp \
../model/timer.cpp 

CPP_DEPS += \
./model/model.d \
./model/quantization.d \
./model/serial_io.d \
./model/timer.d 

OBJS += \
./model/model.o \
./model/quantization.o \
./model/serial_io.o \
./model/timer.o 


# Each subdirectory must supply rules for building sources it contributes
model/%.o: ../model/%.cpp model/subdir.mk
	@echo 'Building file: $<'
	@echo 'Invoking: MCU C++ Compiler'
	arm-none-eabi-c++ -DCPU_MCXN947VDF -DCPU_MCXN947VDF_cm33 -DCPU_MCXN947VDF_cm33_core0 -DARM_MATH_CM33 -D__FPU_PRESENT=1 -DTF_LITE_STATIC_MEMORY -DSERIAL_PORT_TYPE_UART=1 -DSDK_DEBUGCONSOLE=1 -D__MCUXPRESSO -D__USE_CMSIS -DDEBUG -D__NEWLIB__ -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/drivers" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/device" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/utilities/debug_console" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/component/uart" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/utilities/debug_console/config" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/component/serial_manager" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/component/lists" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/device/periph" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/utilities" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/CMSIS" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/CMSIS/m-profile" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/utilities/str" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/board" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/source" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/tensorflow/tensorflow_headers" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/tensorflow/third_party_headers/cmsis/CMSIS/Core/Include" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/tensorflow/third_party_headers/cmsis_nn/Include" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/tensorflow/third_party_headers/flatbuffers/include" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/tensorflow/third_party_headers/gemmlowp" -I"/home/bruno/ufrgs/tcc/automator/cpp-project/tflite-test/model" -O0 -fno-common -g3 -gdwarf-4 -Wall -c -ffunction-sections -fdata-sections -fno-builtin -fno-rtti -fno-exceptions -fmerge-constants -fmacro-prefix-map="$(<D)/"= -mcpu=cortex-m33 -mfpu=fpv5-sp-d16 -mfloat-abi=hard -mthumb -D__NEWLIB__ -fstack-usage -specs=nano.specs -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.o)" -MT"$(@:%.o=%.d)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


clean: clean-model

clean-model:
	-$(RM) ./model/model.d ./model/model.o ./model/quantization.d ./model/quantization.o ./model/serial_io.d ./model/serial_io.o ./model/timer.d ./model/timer.o

.PHONY: clean-model

