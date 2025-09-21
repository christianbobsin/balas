#pragma once
#include <cstdint>

#define INPUT_SIZE GEN_INPUT_SIZE

class ModelInput {
public:
    float data[INPUT_SIZE];
    int size;
    ModelInput() : size(INPUT_SIZE) {}
};
