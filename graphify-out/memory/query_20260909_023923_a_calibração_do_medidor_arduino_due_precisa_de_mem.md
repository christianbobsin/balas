---
type: "query"
date: "2026-09-09T02:39:23.975166+00:00"
question: "A calibração do medidor Arduino Due precisa de memória externa?"
contributor: "graphify"
outcome: "corrected"
correction: "Remover a EEPROM proposta anteriormente. Usar constantes de calibração compiladas e gravadas na Flash do Arduino Due."
source_nodes: ["Firmware autonomo de medicao", "Shunts Kelvin Caddock SR10 HIGH e LOW"]
---

# Q: A calibração do medidor Arduino Due precisa de memória externa?

## Answer

Expanded from original query via vocab: [arduino, firmware, corrente, medicao, shunt]. Não. O ganho efetivo de cada faixa é obtido com o Fluke, inserido como constante no firmware, recompilado e gravado na Flash do próprio Arduino Due.

## Outcome

- Signal: corrected
- Correction: Remover a EEPROM proposta anteriormente. Usar constantes de calibração compiladas e gravadas na Flash do Arduino Due.

## Source Nodes

- Firmware autonomo de medicao
- Shunts Kelvin Caddock SR10 HIGH e LOW