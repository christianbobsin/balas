## Resumo do Capítulo 2 — Principais pontos

* **Redes neurais artificiais (ANNs/DNNs):** explica o que são redes neurais, como neurônios calculam saídas (produto interno + viés + função de ativação) e como isso se organiza em **camadas**. Diferencia as fases de **treinamento** (ajuste de pesos) e **inferência** (uso do modelo já treinado), sendo a inferência o foco do trabalho.

* **Operadores/camadas mais comuns:** descreve as camadas típicas usadas em DNNs, especialmente as mais relevantes para TinyML, como:

  * **Fully Connected (densa)**
  * **Convolution / Depthwise Convolution**
  * **Pooling**
  * **Batch Normalization**
  * **Add (conexões residuais)**
    E também lista funções de ativação comuns (ReLU, sigmoid, tanh, softmax etc.).

* **MACs (Multiply and Accumulate):** apresenta **MACs** como métrica de complexidade computacional (alternativa simplificada a FLOPs), focando no fato de que a maior parte do custo de inferência vem de multiplicações e acumulações. O capítulo mostra como calcular MACs para:

  * camadas **fully connected**
  * **convolução**
  * **depthwise convolution**
    (importante porque MACs é muito usado como “proxy” de latência em NAS e TinyML).

* **Quantização (especialmente int8):** explica quantização como técnica essencial para TinyML por reduzir consumo de **memória** e acelerar inferência, destacando:

  * **Quantization-Aware Training (QAT)** vs **Post-Training Quantization (PTQ)**
  * preferência prática por **PTQ** no cenário de deploy de modelos prontos
  * popularidade de **int8** em TinyML (reduzindo ~4× o tamanho vs float32)
  * noções de **scale factor** e **zero point** para quantizar/desquantizar valores.

* **Neural Architecture Search (NAS) no TinyML:** introduz NAS como busca automática de arquiteturas e ressalta a diferença no TinyML:

  * além de acurácia, é crucial otimizar **latência**, **ROM** e **RAM**
  * NAS “tradicional” tende a gerar modelos grandes demais; por isso surgem abordagens específicas para TinyML.

* **Benchmarking em TinyML e MLPerf Tiny:** apresenta o **MLPerf Tiny** como padrão de benchmark de referência para comparações justas, com:

  * metodologia de medição (múltiplos lotes de inferências, média de tempos)
  * foco em medir **apenas a inferência** (sem pré/pós-processamento)
  * quatro modelos representativos das tarefas comuns:

    1. **Image Classification**
    2. **Visual Wake Words**
    3. **Keyword Spotting**
    4. **Anomaly Detection**
       com uma visão geral das arquiteturas de cada um.

* **Frameworks TinyML (ênfase em TFLM):**

  * Introduz frameworks e aprofunda no **TensorFlow Lite for Microcontrollers (TFLM)**:

    * é **portável** e **minimalista**
    * usa execução baseada em **interpretador**
    * exige configurar o **OpResolver** (listar operadores usados para não linkar tudo)
    * exige definir o tamanho da **tensor arena** (memória estática para tensores intermediários)
    * destaca o problema prático: **estimar a tensor arena é difícil** e pode exigir tentativa e erro.
  * Apresenta o **STM32Cube.AI** como alternativa proprietária para STM32, com geração de código otimizado e ferramentas auxiliares (incluindo ajuda para estimar arena).
