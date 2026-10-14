# Por que a NUCLEO-G474RE foi escolhida para a aquisicao

Revisao: 2026-09-03

## 1. Correcao da comparacao anterior

A versao anterior deste documento afirmou que a placa Arduino discutida era um
`Uno R3`. Isso nao estava sustentado pelo historico do projeto e foi uma
suposicao incorreta. A comparacao com o Uno foi removida.

O modelo exato anteriormente cogitado nao aparece nos documentos nem no
historico disponivel. Pela lembranca de um ADC com mais bits, os candidatos
mais plausiveis sao:

- `Arduino GIGA R1 WiFi`;
- `Arduino Portenta H7`.

Os dois usam o `STM32H747`, que possui tres ADCs com resolucao configuravel de
ate `16 bits` e taxa de ate `3,6 MS/s` nas condicoes indicadas no datasheet.
Portanto, seria incorreto dizer que uma placa Arduino avancada e incapaz de
fazer esta medicao. Se o modelo lembrado for confirmado, a decisao pode ser
reavaliada com a pinagem real.

## 2. Resposta curta

A `NUCLEO-G474RE` continua sendo a referencia do primeiro medidor porque o
caminho necessario esta documentado e e direto:

- `ADC1` e `ADC2` podem operar em modo dual simultaneo;
- cada ADC atinge `4 MS/s` em `12 bits`;
- um timer dispara os dois conversores no mesmo instante;
- o resultado combinado vai para RAM por DMA;
- `A0/PA0` e `A1/PA1` estao expostos em headers padrao Arduino Uno V3;
- o ST-LINK integrado permite programar e depurar sem equipamento adicional.

A escolha nao significa que `12 bits` sejam melhores que `16 bits`. Para
capturar pulsos curtos, simultaneidade, taxa sustentada, trigger e DMA sao tao
importantes quanto a quantidade nominal de bits.

## 3. O que o medidor realmente exige

O `AMC3302EVM` fornece duas saidas analogicas:

```text
Vdiff = OUTP - OUTN
I = (Vdiff - Vzero) / (41 * Rshunt)
```

O sistema de aquisicao precisa:

1. ler `OUTP` e `OUTN` no mesmo instante;
2. manter pelo menos alguns milhões de pares por segundo;
3. usar timer de hardware, sem `delay()` ou laço de software;
4. mover os pares para RAM por DMA;
5. guardar pre-trigger e pos-trigger sem transmitir pela serial durante o
   evento;
6. exportar a captura apenas depois de o DMA parar.

Uma resolucao anunciada de `16 bits` atende apenas parte do requisito. Ela nao
garante dois canais simultaneos, taxa maxima na resolucao escolhida, acesso
simples ao DMA nem 16 bits efetivos em presenca de ruido.

## 4. Comparacao honesta das candidatas

| Recurso | Arduino GIGA R1 WiFi | Arduino Portenta H7 | NUCLEO-G474RE |
| --- | --- | --- | --- |
| MCU | `STM32H747XI`, M7 `480 MHz` + M4 `240 MHz` | `STM32H747`, M7 `480 MHz` + M4 `240 MHz` | `STM32G474RE`, M4 `170 MHz` |
| ADC do MCU | tres ADCs, ate `16 bits`, ate `3,6 MS/s` em condicoes especificas | mesmo MCU e capacidade analogica | cinco ADCs de `12 bits`, ate `4 MS/s` |
| Simultaneidade | possivel no MCU, mas precisa ser confirmada nos pinos expostos e implementada abaixo da API Arduino comum | possivel no MCU, com a mesma necessidade de confirmar pinos | pares `ADC1/2` e `ADC3/4` documentados em modo dual |
| DMA e timer | existem no MCU; exigem implementacao especifica STM32H7/Mbed, alem de cuidado com cache | existem no MCU; mesma complexidade | caminho STM32Cube direto, com registrador combinado do modo dual |
| Memoria | ampla | ampla | `128 KB`, suficiente para o buffer inicial de `32 KB` |
| Conector para laboratorio | headers `2,54 mm`, formato Mega/Due | conectores de alta densidade; normalmente exige carrier | Arduino Uno V3 e ST Morpho, ambos `2,54 mm` |
| Depurador | programacao USB da placa; depuracao depende da configuracao usada | depende de carrier/interface escolhida | ST-LINK integrado |
| Complexidade nao usada | radio, dois cores, camera/display, Mbed OS | dois cores e conectores de alta densidade | perifericos analogicos focados no problema |

O `Arduino GIGA R1 WiFi` e a alternativa Arduino mais compativel com montagem
de bancada: tem headers de `2,54 mm` e ADC superior em resolucao nominal. A
`Portenta H7` e menos conveniente mecanicamente porque normalmente requer uma
carrier board.

## 5. Por que mais bits nao decidiram a escolha

Com referencia de `3,3 V`, o passo ideal de um ADC de 12 bits e:

```text
3,3 V / 4096 = 0,806 mV por codigo
```

No medidor isso representa, antes do ruido e da calibracao:

- cerca de `0,197 mA/codigo` com shunt de `0,1 ohm`;
- cerca de `19,7 uA/codigo` com shunt de `1 ohm`.

Um ADC de 16 bits reduz o passo ideal por um fator de 16, mas o ganho real
depende de ENOB, ruido da referencia, ruido do EVM, casamento entre canais,
layout PTH e taxa escolhida. Como o objetivo imediato e detectar aumento de
consumo e caracterizar pulsos, a estrategia e:

1. validar primeiro tempo de resposta e repetibilidade em `12 bits / 4 MS/s`;
2. medir o ruido real e o menor `delta_I` detectavel;
3. somente entao decidir se 16 bits trazem ganho pratico.

## 6. Janela temporal

O modo `BURST` previsto usa:

```text
8192 pares * 4 bytes = 32768 bytes
8192 / 4.000.000 = 2,048 ms
```

Cada par tem os dois canais do mesmo evento de timer. Em um pulso de `5 us`, a
NUCLEO registra aproximadamente:

```text
5 us / 0,25 us = 20 pares de amostras
```

O `AMC3302` continua limitando a borda analogica a aproximadamente `1 us` a
`1,2 us`. A taxa de `4 MS/s` nao cria informacao acima dessa banda, mas registra
varios pontos da transicao disponivel.

## 7. Motivo pratico para a montagem PTH

A `NUCLEO-G474RE` aceita shield no padrao Arduino Uno V3. Isso permite montar
os dois filtros de ADC e os bornes em uma placa padronizada de passo `2,54 mm`,
com solda PTH. O amplificador SMD fica no `AMC3302EVM` pronto.

Desse modo, a troca para NUCLEO nao obriga uma PCB SMD personalizada. O conjunto
fica dividido em blocos substituiveis:

```text
shunt PTH -> AMC3302EVM pronto -> shield R3 PTH -> NUCLEO-G474RE
```

O diagrama completo esta em
[028_diagrama-montagem-medidor-corrente-pth.md](028_diagrama-montagem-medidor-corrente-pth.md).

## 8. Quando usar o Arduino lembrado

Se a placa original for confirmada como `GIGA R1 WiFi`, ela merece um teste A/B
e pode substituir a NUCLEO se forem demonstrados:

- dois pinos expostos ligados a ADCs que funcionem simultaneamente;
- taxa sustentada escolhida, inclusive em `16 bits` se essa for a vantagem;
- DMA acionado por timer, sem `analogRead()` dentro de loop;
- buffer em regiao de RAM coerente com DMA/cache;
- captura sem perdas e sem trafego USB durante a janela;
- ruido e skew iguais ou melhores que os medidos na G474.

Se for `Portenta H7`, os mesmos testes se aplicam, somados ao custo e a
complexidade da carrier board. Nao ha impedimento tecnico, apenas mais trabalho
de interligacao e validacao.

## 9. Decisao atual

A decisao correta e:

- manter a `NUCLEO-G474RE` como baseline de menor risco de implementacao;
- nao afirmar que ela substituiu um Uno;
- reconhecer `GIGA R1 WiFi`/`Portenta H7` como candidatas de maior resolucao;
- nao comprar uma segunda placa de aquisicao ate identificar o modelo lembrado;
- reavaliar somente com pinagem e captura DMA comprovadas.

Neste texto, `Arduino Uno V3` aparece somente como o nome oficial do padrao
mecanico dos headers da NUCLEO. Isso nao identifica como Uno a placa Arduino
discutida anteriormente.

## 10. Fontes tecnicas

- Arduino, [GIGA R1 WiFi](https://docs.arduino.cc/hardware/giga-r1-wifi):
  `STM32H747XI`, headers de prototipagem e recursos avancados de ADC/DAC;
- Arduino, [Portenta H7](https://docs.arduino.cc/hardware/portenta-h7/):
  `STM32H747` e arquitetura dual-core;
- ST, [STM32H747XI](https://www.st.com/en/microcontrollers-microprocessors/stm32h747xi.html)
  e [datasheet STM32H747](https://www.st.com/resource/en/datasheet/stm32h747xi.pdf):
  tres ADCs, resolucao maxima de 16 bits e taxas por resolucao;
- ST, [STM32G474RE](https://www.st.com/en/microcontrollers-microprocessors/stm32g474re.html)
  e [manual STM32G4](https://www.st.com/resource/en/reference_manual/dm00355726-stm32g4-series-reference-manual-stmicroelectronics.pdf):
  ADCs de `4 MS/s`, modo dual, DMA e timers;
- ST, [NUCLEO-G474RE](https://www.st.com/en/evaluation-tools/nucleo-g474re.html)
  e [esquematico MB1367](https://www.st.com/resource/en/schematic_pack/mb1367-g474re-d01-schematic.pdf):
  ST-LINK, Arduino Uno V3, ST Morpho e pinagem;
- TI, [AMC3302EVM](https://www.ti.com/tool/AMC3302EVM): saida diferencial
  isolada usada pelo medidor.
