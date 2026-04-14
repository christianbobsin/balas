# Phase 1 Image Classification

Subarvore reservada para a Fase 1 da reproducao do experimento de `image_classification`.

Estrutura esperada:

- `generated/float_models/`: modelos Keras gerados a partir da grade do PDF
- `generated/quantized_models/`: `.tflite` quantizados a partir dos modelos float
- `generated/profiling_dataset/`: amostras `.bin` em `float32` para envio pela serial
- `generated/manifests/`: manifestos para o runner de benchmark

Essa subarvore gerada esta ignorada no Git.
