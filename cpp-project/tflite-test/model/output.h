#pragma once
#include <cstdint>

#define OUTPUT_SIZE 10

class ModelOutput {
public:
    float data[OUTPUT_SIZE];
    int size;
    unsigned long inference_time_us;
    ModelOutput() : size(OUTPUT_SIZE) {}
};
