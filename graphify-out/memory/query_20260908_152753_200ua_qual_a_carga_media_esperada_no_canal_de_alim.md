---
type: "query"
date: "2026-09-08T15:27:53.992512+00:00"
question: "200uA qual a carga media esperada no canal de alimentação dos socs ? 200uA não é muito alto ?"
contributor: "graphify"
outcome: "useful"
source_nodes: ["Medicao classe A - rail dedicado", "Shunts Kelvin Caddock SR10 HIGH e LOW", "Nordic nRF52840 Cortex-M4F", "Relatorio de desempenho STM32 vs NXP"]
---

# Q: 200uA qual a carga media esperada no canal de alimentação dos socs ? 200uA não é muito alto ?

## Answer

Expanded from original query via vocab: [corrente, medicao, micro, power, rail, supply, low, board, nordic, nxp, stm]. Os 200 uA não são a carga média esperada, mas o limite inferior nominal derivado de 10 mV na saída com INA180A2, ganho 50 e shunt de 1 ohm. Para inferência ativa, as referências de ordem de grandeza são nRF52840 cerca de 3,3 mA a 64 MHz, MCXN947 pelo menos 8,55 mA na condição publicada de 57 uA/MHz a 150 MHz, e STM32H723 cerca de 99 a 145 mA a 550 MHz conforme execução/cache. Logo a faixa serve ao consumo ativo, mas é inadequada para sleep: Nordic abaixo de poucos uA, NXP 2 a 6 uA, e STM32 em standby de poucos uA. Para energia média com baixo duty cycle, usar PPK2 ou um front-end específico de microcorrente.

## Outcome

- Signal: useful

## Source Nodes

- Medicao classe A - rail dedicado
- Shunts Kelvin Caddock SR10 HIGH e LOW
- Nordic nRF52840 Cortex-M4F
- Relatorio de desempenho STM32 vs NXP