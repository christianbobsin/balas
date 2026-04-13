# Testdata

## Objetivo

Este diretorio existe para guardar fixtures pequenas e versionadas que ajudem a validar o projeto de forma reproduzivel.

O que faz sentido colocar aqui:

- um modelo `.tflite` pequeno e conhecido
- um pequeno conjunto de entradas `.bin` para profiling
- um manifesto com os valores esperados de arena, MACs e observacoes

O que nao faz sentido colocar aqui:

- artefatos gerados pelo MCUXpresso
- `Debug/`, `Release/`, `.metadata/`
- binarios de firmware gerados por build local
- instaladores externos grandes

## Estrutura recomendada

Quando houver um modelo congelado para sanity test, a estrutura recomendada e:

```text
testdata/
  sanity-model/
    model_quant.tflite
    profiling_dataset/
      sample_001.bin
      sample_002.bin
    manifest.json
    README.md
```

## Manifesto sugerido

O `manifest.json` desse fixture deveria registrar pelo menos:

- nome do modelo
- formato de entrada esperado
- quantidade de amostras do dataset
- `arena_size` esperada
- `macs` esperados
- observacoes sobre placa, firmware e protocolo

## Estado atual

No momento, o repositorio ainda nao contem um modelo `.tflite` congelado e validado para testes comparativos.

Por isso:

- os artefatos gerados do workspace foram tratados como lixo de build local
- a estrategia correta daqui para frente e adicionar um fixture pequeno e intencional neste diretorio
