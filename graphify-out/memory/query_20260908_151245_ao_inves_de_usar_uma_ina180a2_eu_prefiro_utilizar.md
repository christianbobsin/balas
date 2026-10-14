---
type: "query"
date: "2026-09-08T15:12:45.297133+00:00"
question: "Ao inves de usar uma INA180A2 eu prefiro utilizar o INA180-181EVM pois esta montagem precisa ser feita em uma protoboard ou ou placa DIP padrão. revise o projeto lvenado isso em consideração."
contributor: "graphify"
outcome: "useful"
source_nodes: ["Medidor autonomo de corrente DC instantanea", "Diagrama de montagem PTH do medidor"]
---

# Q: Ao inves de usar uma INA180A2 eu prefiro utilizar o INA180-181EVM pois esta montagem precisa ser feita em uma protoboard ou ou placa DIP padrão. revise o projeto lvenado isso em consideração.

## Answer

Expanded from graph vocabulary: Arduino, corrente, amplificador, PTH. O projeto Due foi revisado para usar o INA180-181EVM inteiro, canal U2 com INA180A2 de ganho 50, ligado por mini-hooks aos pontos TP211 a TP215. Shunts Kelvin e filtro ficam em placas universais PTH; a corrente do DUT não passa pela protoboard nem pelos pontos de teste. Documentos 029 e 030 atualizados e verificados.

## Outcome

- Signal: useful

## Source Nodes

- Medidor autonomo de corrente DC instantanea
- Diagrama de montagem PTH do medidor