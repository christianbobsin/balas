---
type: "query"
date: "2026-09-08T15:31:16.706508+00:00"
question: "houve algum erro de coneito no conceito da ideia do uso do projeto em 029 ? pois me parece que comentei um erro de julgamento."
contributor: "graphify"
outcome: "useful"
source_nodes: ["Medidor autonomo de corrente DC instantanea", "Modo PROFILE para potencia e energia", "Medicao classe A - rail dedicado", "Medicao classe B - alimentacao externa do SoC", "Shunts Kelvin Caddock SR10 HIGH e LOW"]
---

# Q: houve algum erro de coneito no conceito da ideia do uso do projeto em 029 ? pois me parece que comentei um erro de julgamento.

## Answer

Expanded from original query via graph vocab: [corrente, medicao, micro, low, perfil, profile, burst, energia, rail, power, nordic, stm]. O conceito central do 029 é válido somente como perfilador de corrente ativa em mA durante a inferência. O erro de julgamento foi tratá-lo como alternativa geral de medição de consumo sem fixar primeiro a faixa dinâmica: as três placas cobrem poucos microamperes em sleep até cerca de 145 mA em atividade, amplitude que um único canal fixo INA180A2 mais ADC de 12 bits não cobre com exatidão. A solução também troca o isolamento do projeto 025-028 por terra comum e exige firmware, calibração e montagem, reduzindo a vantagem econômica frente ao PPK2. Há ainda texto histórico desatualizado no 030 sobre low-side, pois o 029 atual já é high-side. Para atividade em mA o Due continua coerente; para sleep mais atividade, PPK2 é a escolha correta; para isolamento e pulsos rápidos, manter AMC3302 mais Nucleo.

## Outcome

- Signal: useful

## Source Nodes

- Medidor autonomo de corrente DC instantanea
- Modo PROFILE para potencia e energia
- Medicao classe A - rail dedicado
- Medicao classe B - alimentacao externa do SoC
- Shunts Kelvin Caddock SR10 HIGH e LOW