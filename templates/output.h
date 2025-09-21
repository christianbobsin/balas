#pragma once
#include <cstdint>

#define OUTPUT_SIZE GEN_OUTPUT_SIZE

class ModelOutput {
public:
    float data[OUTPUT_SIZE];
    int size;
    unsigned long inference_time_us;
    ModelOutput() : size(OUTPUT_SIZE) {}
};
