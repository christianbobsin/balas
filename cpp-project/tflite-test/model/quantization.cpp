#include "quantization.h"
#include <cstdint>

void float32_to_int8(const float *float_values, int8_t *int8_values,
                     int size, float scale, int zero_point) {
    for (int i = 0; i < size; i++) {
        // Apply quantization
        int8_values[i] = (int8_t)round(float_values[i] / scale + zero_point);

        // Clamp to int8 range (-128 to 127)
        if (int8_values[i] > 127) {
            int8_values[i] = 127;
        } else if (int8_values[i] < -128) {
            int8_values[i] = -128;
        }
    }
}

void int8_to_float32(const int8_t* int8_values, float* float32_values, int length, float scale, int zero_point) {
    for (int i = 0; i < length; i++) {
        float32_values[i] = scale * (int8_values[i] - zero_point);
    }
}
