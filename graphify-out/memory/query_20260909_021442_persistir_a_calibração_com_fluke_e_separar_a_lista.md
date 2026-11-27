---
type: "query"
date: "2026-09-09T02:14:42.274029+00:00"
question: "Persistir a calibração com Fluke e separar a lista de compras/mensagem ao orientador em um Markdown local não versionado"
contributor: "graphify"
outcome: "useful"
source_nodes: ["Shunts Kelvin Caddock SR10 HIGH e LOW", "Medidor autonomo de corrente DC instantanea", "Lista de compras do medidor modular PTH"]
---

# Q: Persistir a calibração com Fluke e separar a lista de compras/mensagem ao orientador em um Markdown local não versionado

## Answer

Expanded from original query via vocab: [arduino, corrente, medicao, shunt, shunts, kelvin, compras]. O projeto Due usa uma calibração inicial independente para LOW/1 ohm e HIGH/0,1 ohm; os coeficientes lineares são gravados em EEPROM I2C externa, com verificação rápida antes de campanhas. A lista de compras e a mensagem ao orientador foram movidas para arquivo local excluído do Git.

## Outcome

- Signal: useful

## Source Nodes

- Shunts Kelvin Caddock SR10 HIGH e LOW
- Medidor autonomo de corrente DC instantanea
- Lista de compras do medidor modular PTH