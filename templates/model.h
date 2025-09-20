#pragma once

#include "tensorflow/lite/micro/kernels/micro_ops.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "input.h"
#include "output.h"

#define TENSOR_ARENA_SIZE GEN_TENSOR_ARENA_SIZE
#define N_OPS GEN_N_OPS

class MyModel {
    private:
        const tflite::Model* model;
        tflite::MicroMutableOpResolver<N_OPS> resolver;
        tflite::MicroInterpreter interpreter;
    public:
        MyModel();
        void run_inference(ModelInput& input, ModelOutput& output);
        void print_outputs(ModelOutput& output);
        int get_input_size();
        int get_output_size();
        DataType get_input_type();
        DataType get_output_type();
};



