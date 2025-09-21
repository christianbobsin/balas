#pragma once
#include <cstdint>

#define OUTPUT_SIZE 10

class ModelOutput {
public:
    float* data;
    int size;
    unsigned long inference_time_us;
    ModelOutput(int size) {
        this->data = new float[size];
        this->size = sizeof(data);
    }
};
