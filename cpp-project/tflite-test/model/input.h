#pragma once
#include <cstdint>

#define INPUT_SIZE 3072

class ModelInput {
public:
    float data[INPUT_SIZE];
    int size;
    ModelInput() : size(INPUT_SIZE) {}
};
