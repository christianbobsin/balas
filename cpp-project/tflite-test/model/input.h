#pragma once
#include <cstdint>


class ModelInput {
public:
    float* data;
    int size;
    ModelInput(int size) {
        this->data = new float[size];
        this->size = sizeof(data);
    }
};
