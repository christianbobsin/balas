# Sanity Model Fixture

## Objetivo

Este diretorio reserva um fixture pequeno e controlado para sanity tests reproduziveis do projeto.

Quando um modelo de referencia for escolhido, ele deve ser colocado aqui junto com um conjunto minimo de entradas e um manifesto de metadados.

## Estrutura

```text
testdata/sanity-model/
  README.md
  manifest.json
  model_quant.tflite
  profiling_dataset/
    .gitkeep
```

## O que colocar aqui

- `model_quant.tflite`
  Modelo quantizado pequeno e conhecido, usado como referencia de teste.

- `profiling_dataset/`
  Pequeno conjunto de amostras `.bin` em `float32`, suficiente para validar o protocolo serial e a agregacao do host.

- `manifest.json`
  Metadados esperados do fixture, incluindo arena, MACs e observacoes de uso.

## Critérios para o modelo congelado

O modelo escolhido para este fixture deve:

- ser pequeno o suficiente para build e deploy rapidos
- ter formato de entrada simples
- funcionar de forma estavel no fluxo host + firmware
- ser licitamente versionavel no repositorio

## Fluxo esperado

Quando este fixture estiver populado, o sanity test ideal sera:

1. usar `model_quant.tflite` como entrada do `automator.py`
2. usar `profiling_dataset/` como dataset de profiling
3. comparar o comportamento observado com os valores registrados em `manifest.json`

## Estado atual

Este diretorio foi criado vazio de proposito.

Ainda falta escolher e adicionar:

- um `model_quant.tflite` real
- amostras `.bin` reais em `profiling_dataset/`
- valores preenchidos no `manifest.json`
