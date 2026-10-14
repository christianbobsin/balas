---
type: "query"
date: "2026-10-14T12:11:14.795870+00:00"
question: "preciso do modelo do circuito de medição de energia que preciso montar com o ina e os shunta de 1 e 0.1 ohms"
contributor: "graphify"
outcome: "corrected"
correction: "Expanded from original query via vocab: medicao corrente shunt kelvin energia. O grafo ainda aponta para a arquitetura anterior NUCLEO/AMC3302. Conferido no documento atual docs/029_projeto_medicao_corrente_arduino_due.md e no manual TI SBOU183: Arduino Due, INA180-181EVM U2 INA180A2 ganho 50; shunt externo Kelvin no positivo, 1 ohm LOW ate 40 mA ou 0.1 ohm HIGH ate 400 mA, um por vez. TP211=3V3, TP212=sense fonte, TP213=sense DUT, TP214=OUT via 100 ohms para A0, capacitor 10 nF de A0 ao GND, TP215=GND comum. Energia exige tensao no DUT e integracao V*I no tempo. Hardware de corrente ainda requer montagem e calibracao."
source_nodes: ["Shunts Kelvin Caddock SR10 HIGH e LOW"]
---

# Q: preciso do modelo do circuito de medição de energia que preciso montar com o ina e os shunta de 1 e 0.1 ohms

## Answer

Expanded from original query via vocab: medicao corrente shunt kelvin energia. O grafo ainda aponta para a arquitetura anterior NUCLEO/AMC3302. Conferido no documento atual docs/029_projeto_medicao_corrente_arduino_due.md e no manual TI SBOU183: Arduino Due, INA180-181EVM U2 INA180A2 ganho 50; shunt externo Kelvin no positivo, 1 ohm LOW ate 40 mA ou 0.1 ohm HIGH ate 400 mA, um por vez. TP211=3V3, TP212=sense fonte, TP213=sense DUT, TP214=OUT via 100 ohms para A0, capacitor 10 nF de A0 ao GND, TP215=GND comum. Energia exige tensao no DUT e integracao V*I no tempo. Hardware de corrente ainda requer montagem e calibracao.

## Outcome

- Signal: corrected
- Correction: Expanded from original query via vocab: medicao corrente shunt kelvin energia. O grafo ainda aponta para a arquitetura anterior NUCLEO/AMC3302. Conferido no documento atual docs/029_projeto_medicao_corrente_arduino_due.md e no manual TI SBOU183: Arduino Due, INA180-181EVM U2 INA180A2 ganho 50; shunt externo Kelvin no positivo, 1 ohm LOW ate 40 mA ou 0.1 ohm HIGH ate 400 mA, um por vez. TP211=3V3, TP212=sense fonte, TP213=sense DUT, TP214=OUT via 100 ohms para A0, capacitor 10 nF de A0 ao GND, TP215=GND comum. Energia exige tensao no DUT e integracao V*I no tempo. Hardware de corrente ainda requer montagem e calibracao.

## Source Nodes

- Shunts Kelvin Caddock SR10 HIGH e LOW