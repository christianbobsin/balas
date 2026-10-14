---
type: "query"
date: "2026-10-11T14:48:16.614440+00:00"
question: "Qual o sampling rate que vamos alcançar no projeto do medidor Arduino?"
contributor: "graphify"
outcome: "corrected"
correction: "Usar docs/029 e docs/034 para taxa planejada e estado do firmware Arduino Due; o grafo atual reflete a arquitetura anterior."
---

# Q: Qual o sampling rate que vamos alcançar no projeto do medidor Arduino?

## Answer

Expanded via graph vocabulary: arduino adc taxa amostras. O grafo recuperou o projeto anterior com NUCLEO e nao resolveu a taxa do Due. Verificacao direta em docs/029_projeto_medicao_corrente_arduino_due.md secao 8: a meta e 500 kS/s (2 us por amostra), PROFILE com saida filtrada/decimada de 50 ou 100 kS/s; LIMIT ate 1 MS/s somente apos validacao. docs/034_validacao-adc-arduino-due.md esclarece que o firmware atual faz lotes de 64 amostras e 10 relatorios/s, sem aquisicao continua a 500 kS/s. A placa documentada e Arduino Due.

## Outcome

- Signal: corrected
- Correction: Usar docs/029 e docs/034 para taxa planejada e estado do firmware Arduino Due; o grafo atual reflete a arquitetura anterior.