# Projeto de medidor autonomo de corrente DC instantanea

Revisao: 2026-09-03

Status: arquitetura eletrica e roteiro de validacao definidos. A implementacao
de laboratorio recomendada agora usa `AMC3302EVM` pronto e componentes PTH em
placas padronizadas, conforme o documento 028. O circuito ainda nao foi montado
nem validado fisicamente. Nenhuma das tres placas deve ser conectada antes da
aprovacao completa do circuito de carga ficticia deste documento.

Restricao obrigatoria: nenhuma placa BALAS sera soldada, dessoldada, cortada ou
tera ponte de solda alterada. Toda conexao com as placas deve ser removivel. A
solda manual fica restrita ao shield e as placas universais PTH do medidor;
isso nao implica modificar as placas medidas. Uma PCB SMD personalizada passa a
ser apenas uma revisao futura, nao a forma recomendada para o primeiro prototipo.

Este documento sucede o levantamento dos pontos de medicao feito em
[015_medicao-energia-placas-desenvolvimento.md](015_medicao-energia-placas-desenvolvimento.md).

Documentos complementares:

- [026_lista-compras-medidor-corrente-dc.md](026_lista-compras-medidor-corrente-dc.md):
  lista de compras, fornecedores e criterios para cotacao da montagem;
- [027_por-que-nucleo-g474re-em-vez-de-arduino.md](027_por-que-nucleo-g474re-em-vez-de-arduino.md):
  correcao da comparacao com Arduino e justificativa da placa de aquisicao;
- [028_diagrama-montagem-medidor-corrente-pth.md](028_diagrama-montagem-medidor-corrente-pth.md):
  diagrama de ligacao, pinagem e montagem PTH em placas padronizadas.

## 1. Objetivo

Construir um instrumento que:

- meca a corrente no rail do microcontrolador da `FRDM-MCXN947`, da
  `NUCLEO-H723ZG` e da `nRF52840-DK`;
- detecte aumentos de consumo causados pelo inicio ou pela intensificacao do
  processamento;
- capture transientes curtos sem depender de osciloscopio;
- mantenha o computador galvanicamente isolado da placa medida;
- gere amostras e metricas reproduziveis no computador por USB;
- seja validado primeiro com uma carga resistiva controlada, sem usar nenhuma
  das placas do BALAS;
- conecte-se as tres placas sem solda e sem qualquer alteracao permanente.

O instrumento proposto e um medidor por shunt com tres blocos:

1. `AMC3302EVM` pronto para amplificar e isolar a tensao do shunt;
2. `NUCLEO-G474RE` dedicada ao instrumento, usando dois ADCs simultaneos,
   timer e DMA;
3. shield Arduino R3 com apenas filtros e bornes PTH.

O trigger inicial sera por limiar de corrente, sem fio GPIO na placa medida. Um
`6N137` DIP-8 pode ser adicionado depois como marcador optico. Um segundo modulo
pronto `AMC3330EVM` pode medir a tensao dinamica do rail, mas nao e obrigatorio
na primeira montagem: inicialmente a tensao media sera registrada com
multimetro para estimar energia.

## 2. O que significa "instantaneo"

Nao existe medicao literalmente instantanea nem garantia de detectar qualquer
variacao de amplitude arbitrariamente pequena. O limite final e imposto por:

- largura de banda do amplificador;
- taxa de amostragem e resolucao do ADC;
- ruido eletrico e erro de offset;
- resistencia e indutancia de shunt, trilhas e cabos;
- capacitores de desacoplamento existentes depois do ponto de medicao.

O `AMC3302` tem largura de banda tipica de `340 kHz` e minima especificada de
`290 kHz`. A aproximacao `tr = 0,35 / BW` produz tempo de subida entre cerca de
`1,0 us` e `1,2 us`. Os ADCs do `STM32G474` podem operar a `4 MS/s`, ou uma
amostra a cada `250 ns`.

Meta realista do primeiro prototipo:

- enxergar a borda de um aumento na ordem de `1 us` a `2 us`;
- medir com confianca o patamar de pulsos com `5 us` ou mais;
- medir toda a inferencia em um segundo modo, com menor taxa e janela longa;
- definir o menor aumento detectavel somente depois de medir o ruido real.

Os transientes internos do silicio podem ser mais rapidos. O medidor observa a
corrente reposta pelo rail no ponto da placa, nao cada comutacao interna do
processador.

## 3. Arquitetura do instrumento

```text
LADO DA PLACA/CARGA                BARREIRA             LADO DO MEDIDOR/PC

RAIL_IN --[SHUNT PTH Kelvin]-- RAIL_OUT/MCU
               |   |
               |   +-- INN + HGND --+
               +------ INP ---------| AMC3302EVM ||====|| OUTP -- A0/ADC1
                                     | pronto      ||====|| OUTN -- A1/ADC2
                                     +------------+       GND --- GND_MEDIDOR

                                               shield Arduino R3 PTH
                                                     |
                                               NUCLEO-G474RE
                                               timer + ADC + DMA
                                                     |
                                               USB/VCOM para PC
```

A corrente que alimenta o MCU atravessa somente o shunt. Ela nao atravessa um
optoacoplador, diodo ou regulador adicional. A isolacao ocorre depois da
conversao da queda de tensao e por isso nao acrescenta a queda direta de um
optoacoplador ao rail.

O USB e o terra do computador existem apenas no lado direito das barreiras. O
lado de entrada do `AMC3302EVM` flutua junto com o rail medido. O diagrama
pino a pino esta no documento 028.

### 3.1 O que efetivamente protege as placas

Um optoacoplador comum nao deve ficar em serie com a alimentacao do MCU: sua
queda de tensao e sua corrente alterariam justamente o que se pretende medir.
A protecao e dividida da seguinte forma:

- `AMC3302EVM` isola galvanicamente o canal analogico de corrente;
- o trigger inicial e interno, por limiar, e nao cria outro caminho de terra;
- o `AMC3330EVM` e o optoacoplador `6N137` podem ser adicionados depois;
- o computador nunca compartilha terra com a placa medida;
- toda fonte do DUT deve ter saida flutuante em relacao ao computador, ou a
  isolacao seria contornada por outro cabo;
- conectores polarizados, contatos isolados e alivio de tracao evitam contato
  acidental;
- toda primeira energizacao usa fonte com limite de corrente e sobretensao;
- nenhum capacitor, diodo de protecao ou carga adicional e colocado depois do
  shunt sem ser contabilizado.

O caminho `RAIL_IN -> shunt -> RAIL_OUT` continua sendo condutivo por projeto.
A isolacao protege a interface de aquisicao e o computador; ela nao corrige
polaridade errada nem tensao excessiva aplicada ao DUT. Por isso a polaridade e
a tensao precisam ser confirmadas com multimetro antes de conectar a placa.

## 4. Faixas de corrente

O shunt deve ficar em uma pequena placa filha removivel, com quatro terminais
Kelvin. Nunca selecionar ou trocar a faixa com o dispositivo energizado.

| Faixa | Shunt | Faixa linear teorica | Faixa nominal recomendada | Escala analogica | Uso inicial |
| --- | --- | --- | --- | --- | --- |
| `HIGH` | `0,100 ohm`, PTH Kelvin, valor calibrado | `0` a `500 mA` | ate `400 mA` | `4,1 mV/mA` | FRDM-MCXN947 e NUCLEO-H723ZG |
| `LOW` | `1,000 ohm`, PTH Kelvin, valor calibrado | `0` a `50 mA` | ate `40 mA` | `41 mV/mA` | nRF52840-DK por `P21` e correntes baixas confirmadas |

O limite vem da faixa linear de `+50 mV` do `AMC3302`:

```text
Vshunt = I * Rshunt
Vout_diff = VOUTP - VOUTN = 41 * Vshunt
I = (Vout_diff - Vzero) / (41 * Rshunt)
```

Exemplos:

| Corrente | `Vout_diff` com `0,1 ohm` | `Vout_diff` com `1 ohm` |
| ---: | ---: | ---: |
| `1 mA` | `4,1 mV` | `41 mV` |
| `10 mA` | `41 mV` | `410 mV` |
| `40 mA` | `164 mV` | `1,64 V` |
| `200 mA` | `820 mV` | fora da faixa |

Na revisao PTH, usar Caddock `SR10-0.10-1%` e `SR10-1.00-1%`, ambos com quatro
terminais. A tolerancia inicial de `1%` e removida do ganho pela calibracao de
cada modulo; a incerteza residual deve ser medida, nao presumida.

O shunt `1 ohm` nunca deve ser usado na STM32 antes de confirmar, com a faixa
`HIGH`, que o pico fica abaixo de `40 mA`. A margem de `20%` evita trabalhar no
limite do amplificador.

## 5. Circuito do canal de corrente

Na primeira montagem, esta secao e implementada pelo `AMC3302EVM` pronto. O EVM
ja contem `AMC3302`, conversor isolado, desacoplamentos, ferrites, filtro de
entrada e bornes. Nao reproduzir esses componentes SMD em placa universal. As
informacoes abaixo ficam como requisito eletrico para uma eventual PCB propria.

### 5.1 Caminho de potencia e conexoes Kelvin

Use um conector de entrada com chave mecanica e dois contatos de corrente:

- `RAIL_IN`: lado da fonte da placa;
- `RAIL_OUT`: lado que segue para o MCU.

O shunt de quatro terminais fica entre eles. Os dois terminais externos
conduzem corrente. Os dois terminais internos seguem por trilhas simetricas aos
resistores de entrada do amplificador. Nao retirar o sinal Kelvin dos conectores
ou das trilhas de potencia.

Na revisao modular, usar diretamente a pinagem do EVM:

| Borne do EVM | Ligacao |
| --- | --- |
| `J2.1 INP` | terminal Kelvin de `RAIL_IN` |
| `J2.2 INN` | terminal Kelvin de `RAIL_OUT` |
| `J2.3 HGND` | mesmo terminal Kelvin de `RAIL_OUT` |
| `J3.2 OUTP` | shield PTH e `A0/PA0/ADC1_IN1` |
| `J3.1 OUTN` | shield PTH e `A1/PA1/ADC2_IN2` |
| `J3.3 GND` | `GND_MEDIDOR` |
| `J1.1 VDD` | `5 V` da NUCLEO |
| `J1.2 GND` | `GND_MEDIDOR` |

Para uma futura PCB personalizada, a conexao do `AMC3302` avulso seria:

| Pino funcional | Ligacao |
| --- | --- |
| `INP` | Kelvin de `RAIL_IN` por `10 ohm`, `0,1%`. |
| `INN` | Kelvin de `RAIL_OUT` por `10 ohm`, `0,1%`. |
| filtro diferencial | `10 nF`, C0G/NP0, diretamente entre `INP` e `INN` depois dos resistores. |
| `HGND` | Trilha Kelvin separada ate o terminal externo de `RAIL_OUT`, conforme o datasheet. |
| `OUTP` | Entrada analogica de `ADC1` no medidor. |
| `OUTN` | Entrada analogica de `ADC2` no medidor. |
| `VDD/GND` | `3,3 V` ou `5 V` somente do lado da NUCLEO-G474RE. |

O filtro `10 ohm + 10 nF + 10 ohm` tem corte diferencial aproximado de
`796 kHz`, acima da largura de banda do `AMC3302`. Ele reduz ruido do modulador
sem ser o gargalo temporal do prototipo.

Copiar integralmente do datasheet os capacitores de desacoplamento de
`DCDC_IN`, `DCDC_OUT`, `HLDO_OUT`, `LDO_OUT` e `VDD`. Os capacitores de `1 nF`
devem ser C0G/NP0 e ficar imediatamente junto aos pinos. Nao omitir o indutor ou
ferrite bead indicado no caminho do conversor DC/DC.

### 5.2 Layout obrigatorio

- shunt e resistores de `10 ohm` o mais perto possivel do `AMC3302`;
- pares Kelvin curtos, simetricos e afastados das linhas digitais;
- nenhum plano, trilha ou cobre sob a barreira de isolacao;
- respeitar os `8 mm` de creepage/clearance do encapsulamento e do layout de
  referencia, mesmo que o DUT opere em baixa tensao;
- separar fisicamente `DUT_SIDE` e `PC_SIDE` na serigrafia;
- manter os clocks do STM32 e o conector USB longe do shunt e de `INP/INN`;
- usar ponto de teste em `OUTP`, `OUTN` e `VREF_ADC`.

## 6. Canal isolado de tensao do rail, opcional

Na primeira montagem, registrar a tensao do rail com multimetro antes e depois
da captura e calcular energia com a tensao media. Se a variacao passar de `1%`,
implementar este canal com um `AMC3330EVM` pronto e divisor PTH; nao montar o
`AMC3330` SMD avulso.

O canal de tensao usa `AMC3330`, faixa de entrada `+/-1 V`, ganho nominal `2`
e largura de banda tipica de `375 kHz`.

Divisor recomendado para aceitar ate `5,5 V`:

```text
RAIL_OUT ---- 49,9 kohm ----+---- INP AMC3330
                            |
                           10,0 kohm
                            |
DUT_GND --------------------+---- INN e HGND
```

Use resistores `0,1%`, TCR <= `25 ppm/°C`. A relacao nominal e `5,99:1`:

```text
Vrail = ((VOUTP - VOUTN) - Vzero_v) * 5,99 / 2
```

O divisor consome aproximadamente `55 uA` em `3,3 V` e essa corrente atravessa
o shunt. Para corrente absoluta do DUT, o firmware deve corrigir:

```text
Idut = Ishunt - Vrail / 59,9 kohm
```

Para medir apenas o aumento sobre o baseline, essa carga constante desaparece
na subtracao. Ainda assim, registrar se o canal de tensao estava conectado.

O canal de tensao pode ser amostrado mais lentamente que o de corrente. Ele nao
deve reduzir a taxa de `4 MS/s` do modo `BURST` de corrente.

## 7. Trigger e gerador de teste

### 7.1 Marcador de inferencia

O primeiro firmware usa trigger por limiar de corrente. Isso evita um fio GPIO
extra e qualquer carga eletrica adicional na placa medida.

Se for necessario marcar exatamente `Invoke()`, a expansao PTH usa `6N137` em
`DIP-8`. Ele nao deve ser ligado imediatamente: a corrente do LED pode aparecer
na medicao. Antes do uso real, definir alimentacao, polaridade, sequenciamento e
correcao dessa corrente conforme a secao 7 do documento 028.

### 7.2 Gerador da carga de validacao

Na carga ficticia, usar `SN74HCT14N` PDIP e dois `FQP30N06L` TO-220. Durante
esse teste, e permitido unir `GND_TESTE` ao GND da NUCLEO porque nenhuma placa
BALAS esta conectada. A carga e removida por completo antes do ensaio real. O
diagrama PTH esta na secao 6 do documento 028.

## 8. Aquisicao sem osciloscopio

### 8.1 Placa escolhida

Use uma `NUCLEO-G474RE` dedicada ao medidor. O `STM32G474RE` possui:

- Cortex-M4F a `170 MHz`;
- `128 KB` de SRAM;
- cinco ADCs de `12 bits` capazes de ate `4 MS/s`;
- timers e DMA adequados para amostragem simultanea;
- ST-LINK/VCOM para comandos e exportacao depois da captura.

Essa NUCLEO nao substitui nem alimenta a placa medida. Ela pertence
integralmente ao lado isolado do computador.

### 8.2 Ligacao dos ADCs

Conectar `OUTP` a `A0/PA0/ADC1_IN1` e `OUTN` a
`A1/PA1/ADC2_IN2`. O esquematico MB1367 e a tabela de funcoes do MCU confirmam
esses pinos. Antes de considerar o shield liberado:

1. selecionar `PA0` no `ADC1` e `PA1` no `ADC2` no STM32CubeMX para o
   encapsulamento `STM32G474RETx`;
2. gerar o modo `ADC dual regular simultaneous`;
3. disparar ambos pelo mesmo `TIMx TRGO`;
4. ler o registrador combinado por DMA de `32 bits`.

Conferir novamente o esquematico `MB1367` da revisao efetivamente comprada antes
da solda, pois a ST ja publicou revisoes diferentes da placa.

Em cada entrada ADC, colocar `33 ohm` em serie e `100 pF` C0G para o terra do
medidor, junto ao MCU. `OUTP` e `OUTN` permanecem dentro de aproximadamente
`0,4 V` a `2,5 V`, faixa compativel com ADC a `3,3 V`.

### 8.3 Modos de captura

O firmware do medidor deve oferecer dois modos separados para caber na SRAM.

#### `BURST`

- `4 MS/s` simultaneos em `OUTP` e `OUTN`;
- `8192` pares de amostras, armazenados como palavras de `32 bits`;
- janela total de `2,048 ms`;
- buffer circular com `50%` pre-trigger e `50%` pos-trigger;
- trigger por limiar de corrente ou pelo marcador optico opcional;
- transferencia dos dados somente depois que a captura terminar.

Esse modo ocupa `32 KB` de SRAM e e usado para bordas, picos e pulsos curtos.

#### `PROFILE`

- amostragem entre `50 kS/s` e `100 kS/s` para corrente;
- reducao para `5 kS/s` ou `10 kS/s` por media de blocos;
- acumuladores de `64 bits` para soma, soma de quadrados, pico e energia;
- janela configuravel de ate a duracao completa da inferencia;
- canal de tensao amostrado junto da serie reduzida;
- exportacao depois do fim da inferencia.

Esse modo mede baseline, corrente media, duracao e energia. Ele nao substitui o
`BURST` para caracterizar a borda mais rapida.

### 8.4 Resolucao inicial

Com referencia ADC de aproximadamente `3,3 V`, um ADC de `12 bits` tem passo de
cerca de `0,806 mV` por canal. Antes de considerar ruido e a subtracao entre os
dois ADCs, isso equivale aproximadamente a:

- `0,197 mA/LSB` na faixa `HIGH`;
- `19,7 uA/LSB` na faixa `LOW`.

O firmware deve ler `VREFINT`, calibrar offset dos dois ADCs e medir o desvio do
baseline. O criterio de evento deve ser:

```text
delta_I > max(5 * sigma_baseline, erro_total_calibrado)
```

Nao publicar um limite de deteccao em microamperes antes do ensaio real.

### 8.5 Upgrade opcional de precisao

Depois que o prototipo com ADC interno estiver validado, um `ADS9224R` pode
substituir os ADCs internos. Ele oferece `16 bits`, `3 MS/s` e entrada
diferencial. A troca melhora resolucao e linearidade, mas exige driver, layout,
SPI de alta velocidade e firmware adicionais. Ela quase nao melhora a resolucao
temporal, pois a banda de `290 kHz` a `340 kHz` do `AMC3302` continua sendo o
limite analogico.

## 9. Hardware necessario

### 9.1 Instrumento principal

| Qtd. | Item | Especificacao / funcao |
| ---: | --- | --- |
| 1 | `NUCLEO-G474RE` | Aquisicao, DMA, trigger, processamento e comunicacao. |
| 1 | `AMC3302EVM` | Modulo pronto com amplificador isolado, filtro e bornes. |
| 1 | proto-shield Arduino R3 | Grade `2,54 mm`, headers empilhaveis, somente componentes PTH. |
| 1 | Caddock `SR10-0.10-1%` | Shunt PTH Kelvin da faixa HIGH, `0,100 ohm`, `1 W`. |
| 1 | Caddock `SR10-1.00-1%` | Shunt PTH Kelvin da faixa LOW, `1,000 ohm`, `1 W`. |
| 2 | `33 ohm` e `100 pF` | Filtros PTH das entradas `A0/A1`. |
| varios | bornes plugaveis e fio | Interligacao mecanicamente segura entre os modulos. |
| 1 | USB/VCOM | Cabo para alimentar e ler somente a NUCLEO do medidor. |
| 1 | fonte regulada com protecao contra sobretensao (`OVP`) e limite de corrente | Necessaria na carga ficticia e para alimentar `P21` da Nordic entre `1,7 V` e `3,6 V`; a saida deve ser flutuante em relacao ao PC. |
| 1 | multimetro basico | Continuidade, polaridade, tensao e calibracao estatica. |

O shield deve ter bornes para `OUTP`, `OUTN`, `GND_MEDIDOR`, `5V` e `GND`.
Botoes e LEDs sao opcionais; comandos pela VCOM bastam na primeira versao. A
faixa eletrica vem da placa de shunt fisicamente separada; nao usar chave
analogica em serie com o rail.

### 9.2 Carga ficticia de validacao

| Qtd. | Item | Valor |
| ---: | --- | --- |
| 1 | fonte de bancada | `3,3 V`, limite inicial em `250 mA`. |
| 1 | `RBASE` | `330 ohm`, `1%` ou melhor, `0,25 W`. |
| 1 | `RSTEP1` | `120 ohm`, `1%` ou melhor, `0,5 W`. |
| 1 | `RSTEP2` | `22 ohm`, `1%` ou melhor, `2 W`. |
| 2 | MOSFET N logico | `FQP30N06L`, PTH `TO-220`. |
| 1 | driver de gate | `SN74HCT14N`, PTH `PDIP-14`, com soquete. |
| 2 | resistor de gate | `100 ohm`. |
| 2 | pull-down de gate | `100 kohm`. |
| 1 | placa universal ilhada | FR-4, passo `2,54 mm`, montagem PTH soldada. |

### 9.3 Montagem PTH em placas padronizadas

O front-end SMD e a barreira de isolacao permanecem no `AMC3302EVM` pronto.
Para o restante, a implementacao recomendada e:

1. soldar os filtros e bornes PTH no proto-shield R3;
2. soldar cada shunt Kelvin numa placa universal separada;
3. soldar carga, `SN74HCT14N` em soquete e MOSFETs TO-220 em outra placa;
4. fixar os modulos numa base isolante com espacadores de nylon;
5. usar bornes plugaveis, pares torcidos e etiquetas conforme o documento 028.

Nao usar protoboard sem solda no shunt nem em `OUTP/OUTN`. A montagem PTH
soldada e aceitavel; a restricao de solda continua valendo somente para as tres
placas BALAS.

Os adaptadores de `J24` e `JP4` devem usar receptaculos femea de passo
compativel com os headers existentes e corpo isolante que cubra os contatos. O
adaptador de `P21` deve usar o conector compativel indicado pela revisao fisica
da DK. Nao soldar fios diretamente em nenhuma das tres placas e nao usar garras
metalicas expostas durante captura energizada.

## 10. Circuito de validacao antes das placas

```text
FONTE 3V3
   |
   +---- RAIL_IN [MEDIDOR] RAIL_OUT ----+---- RBASE 330R ------- GND
                                        |
                                        +---- RSTEP1 120R -- Q1 -- GND
                                        |
                                        +---- RSTEP2  22R -- Q2 -- GND

NUCLEO D6 -- 2 inversores SN74HCT14N -- 100R -- gate Q1 -- 100k -- GND_TESTE
NUCLEO D7 -- 2 inversores SN74HCT14N -- 100R -- gate Q2 -- 100k -- GND_TESTE
```

O `SN74HCT14N` e alimentado pelos `5 V` da NUCLEO e recebe `100 nF` PTH entre
os pinos 14 e 7. Na carga ficticia apenas, `GND_TESTE` e o GND da NUCLEO sao
unidos. Nunca repetir essa uniao com uma placa BALAS. Ver o esquema completo e
a pinagem dos MOSFETs no documento 028.

Correntes nominais, antes de considerar tolerancia e `RDS(on)`:

| Estado | Corrente calculada em `3,3 V` | `Vout_diff` na faixa HIGH |
| --- | ---: | ---: |
| somente `RBASE` | `10,0 mA` | `41 mV` |
| `RBASE + RSTEP1` | `37,5 mA` | `154 mV` |
| `RBASE + RSTEP2` | `160,0 mA` | `656 mV` |
| todos ligados | `187,5 mA` | `769 mV` |

Na faixa `LOW`, usar somente `RBASE` e `RSTEP1`. Os outros estados excedem a
faixa nominal.

Nao colocar capacitor de carga na primeira validacao dinamica. Depois que o
tempo de resposta for aprovado, repetir com `1 uF` e `10 uF` em `RAIL_OUT` para
observar, de forma controlada, o efeito de desacoplamento que tambem existira
nas placas reais.

## 11. Firmware minimo do medidor

Comandos recomendados pela VCOM:

```text
INFO
ZERO
CAL HIGH <corrente_mA>
CAL LOW <corrente_mA>
SELFTEST
ARM BURST <trigger_mA>
ARM PROFILE <duracao_ms>
EXPORT CSV
```

Funcoes obrigatorias:

- autoteste de faixa dos dois ADCs e deteccao de saturacao;
- calibracao separada de offset de `ADC1` e `ADC2`;
- calibracao de ganho por faixa;
- armazenamento da resistencia real de cada shunt;
- rejeicao da captura quando houver saturacao;
- timeout de trigger;
- registro de taxa, faixa, firmware e calibracao junto aos dados;
- soma em inteiro de `64 bits` ou ponto flutuante duplo para energia;
- exportacao da janela bruta e do perfil reduzido.

Campos minimos do CSV:

```text
board,firmware_commit,mode,range,r_shunt_ohm,sample_rate_hz,
time_us,current_ma,rail_v,trigger,baseline_ma,delta_ma,power_mw
```

O resumo de cada inferencia deve conter:

- corrente media do baseline;
- desvio padrao do baseline;
- corrente media durante a inferencia;
- pico de corrente;
- `delta` de pico sobre o baseline;
- duracao pelo marcador isolado;
- energia integrada em `mJ`;
- numero de amostras saturadas ou perdidas.

## 12. Validacao do instrumento

### 12.1 Inspecao sem energia

1. Confirmar que nao ha curto entre `RAIL_IN`, `RAIL_OUT` e `DUT_GND`.
2. Medir a resistencia de cada shunt pelo metodo de quatro fios, se o multimetro
   permitir; caso contrario, calibrar pela corrente conhecida.
3. Confirmar resistencia maior que `10 Mohm` entre o terra do DUT e o terra
   USB/NUCLEO.
4. Confirmar orientacao e polaridade de todos os integrados.
5. Confirmar que nao existe cobre sob as barreiras de isolacao.

### 12.2 Validacao estatica

1. Limitar a fonte a `50 mA` e testar `RBASE` na faixa `LOW`.
2. Comparar corrente calculada por tensao/resistencia, multimetro e medidor.
3. Repetir com `RSTEP1`, sem ultrapassar `40 mA` nominal na faixa `LOW`.
4. Trocar para `HIGH`, elevar o limite para `250 mA` e testar os quatro estados.
5. Medir `RAIL_OUT` e a queda no shunt.

Criterios de aceitacao depois de `ZERO` e calibracao:

- erro <= `1%` entre `10 mA` e `200 mA` na faixa `HIGH`;
- erro <= `1%` entre `1 mA` e `40 mA` na faixa `LOW`;
- queda no shunt dentro de `10%` do valor calculado;
- nenhuma saturacao de entrada ou saida;
- `RAIL_OUT` estavel durante pelo menos `10 minutos`.

### 12.3 Validacao dinamica autonoma

Gerar pelo timer da NUCLEO pulsos de:

```text
1 us, 2 us, 5 us, 10 us, 100 us, 1 ms e 100 ms
```

Para cada largura, salvar pelo menos `30` capturas `BURST`. O MOSFET e o
`SN74HCT14N` sao muito mais rapidos que o canal de corrente, portanto a borda
da carga serve como excitacao do teste.

Criterios iniciais:

- pulsos de `5 us` claramente distinguiveis do baseline;
- tempo de subida de `10%` a `90%` <= `2 us` no pulso de `100 us`;
- erro de largura <= `2 us` para pulsos de `10 us` ou maiores;
- overshoot ou ringing <= `10%` do patamar;
- nenhuma amostra perdida no DMA;
- repetibilidade de pico com coeficiente de variacao <= `5%`.

O pulso de `1 us` e exploratorio. Ele pode aparecer atenuado pela largura de
banda e nao e criterio de reprovacao.

### 12.4 Condicao de liberacao

Somente liberar o medidor para as placas quando todos os itens seguintes forem
verdadeiros:

- inspecao sem energia aprovada;
- isolamento DC aprovado;
- duas faixas calibradas;
- teste dinamico de `5 us` aprovado;
- `SELFTEST` repetido apos aquecimento;
- conexoes de cada adaptador conferidas contra o esquematico;
- nenhuma placa exige corte, solda, dessolda ou remocao de componente SMD;
- firmware e coeficientes de calibracao versionados.

## 13. Conexao nas tres placas

Ordem recomendada de validacao real:

1. `FRDM-MCXN947`, porque `J24` nao requer corte de trilha;
2. `NUCLEO-H723ZG`, porque `JP4` tambem e reversivel;
3. `nRF52840-DK` pela entrada externa `P21`, usando somente `SW6`, `SW9` e
   `SW10`. `SB40` e `SB41` nao serao alterados.

### 13.1 Procedimento comum

1. Gravar primeiro o firmware autonomo de ensaio.
2. Desligar e desconectar a placa.
3. Desconectar todos os cabos de dados e usar apenas fonte flutuante com limite
   de corrente em uma entrada de alimentacao aprovada no manual da placa.
4. Instalar a placa de shunt correta com o medidor desligado.
5. Conectar `RAIL_IN`, `RAIL_OUT` e `DUT_GND`. Na Nordic,
   `RAIL_IN` recebe a fonte externa e `RAIL_OUT` alimenta `P21`.
6. Testar continuidade e ausencia de curto.
7. Ligar primeiro a NUCLEO do medidor e executar `ZERO`.
8. Energizar a placa medida com o limite de corrente ativo.
9. Confirmar a tensao em `RAIL_OUT` antes de iniciar a inferencia.
10. Capturar primeiro `PROFILE`, depois `BURST`.
11. Desligar tudo antes de trocar placa, faixa ou adaptador.

### 13.2 Adaptadores

| Placa | `RAIL_IN` | `RAIL_OUT` | Faixa inicial |
| --- | --- | --- | --- |
| FRDM-MCXN947 | `J24-1 / IDD_IN` | `J24-2 / IDD_OUT` | `HIGH` |
| NUCLEO-H723ZG | pino `VDD` de `JP4` | pino `VDD_MCU` de `JP4` | `HIGH` |
| nRF52840-DK em `VDD` | positivo da fonte externa regulada em `3,0 V` | positivo de `P21`; retorno comum ao `GND` de `P21` | `LOW`, apos confirmar o pico em `HIGH` |

Cada chicote deve ter chave mecanica, etiqueta nos dois extremos e teste de
continuidade registrado. Nao usar jumpers Dupont soltos na medicao definitiva.

Na Nordic, colocar `SW9 = VDD`, `SW10 = ON` (`VEXT -> nRF`) e `SW6 = nRF ONLY`
antes de energizar. Confirmar a polaridade marcada de `P21` com multimetro e
esquematico. O caminho `P22/SB40` isolaria `VDD_nRF` de forma mais direta, mas
exige cortar a ponte original e, por isso, esta fora deste projeto.

Classificar NXP e ST como medicao `A - rail dedicado`. Classificar Nordic como
`B - alimentacao externa do SoC`: ela e adequada para `delta_I` e energia
incremental sem adulterar a placa, mas pode conter fuga residual ou outra carga
que permaneca ligada ao dominio `VDD`. Nao misturar os valores absolutos das
duas classes sem registrar essa limitacao.

## 14. Firmware autonomo nas placas BALAS

Para uma comparacao limpa, cada placa precisa de um modo de ensaio que:

- contenha o mesmo tensor de entrada na Flash;
- aguarde botao, GPIO ou temporizador local;
- opcionalmente acione um marcador em torno de `interpreter->Invoke()` ou da
  chamada equivalente, somente depois de o circuito optico ser validado;
- repita a mesma entrada um numero configurado de vezes;
- nao escreva logs, CSV ou dados na UART durante a janela medida.

Isso e especialmente importante na nRF52840-DK. A Nordic informa que a medicao
fica pouco confiavel com terminal ligado a VCOM e recomenda desconectar a USB do
interface MCU depois da programacao. Medir o protocolo serial atual do BALAS
pode ser util para diagnostico, mas nao deve ser confundido com a medicao
comparativa final.

## 15. Plano de construcao

### Etapa A - prototipo de bancada

- adquirir NUCLEO-G474RE, `AMC3302EVM` pronto e componentes PTH;
- montar o proto-shield R3 e a carga em placa universal conforme o documento
  028;
- montar as duas placas de shunt PTH Kelvin;
- implementar `ZERO`, `SELFTEST` e `BURST`;
- aprovar a carga ficticia.

### Etapa B - perfil completo

- implementar `PROFILE` e integracao de energia;
- implementar exportacao CSV;
- validar `30` repeticoes por estado da carga;
- congelar o formato de dados e os coeficientes.

### Etapa C - placas reais

- fabricar os tres chicotes;
- adicionar o modo autonomo aos tres firmwares;
- validar NXP, depois ST e por ultimo Nordic pela entrada `P21`;
- executar a mesma entrada e registrar todas as condicoes.

### Etapa D - melhoria opcional

- adicionar `AMC3330EVM` se a tensao do rail variar mais de `1%`;
- adicionar `6N137` DIP apenas se o marcador exato for necessario;
- avaliar `ADS9224R` somente se a resolucao de `12 bits` for insuficiente;
- comparar ganho de resolucao contra ruido real do `AMC3302`;
- manter o prototipo G474 como referencia de validacao.

## 16. Fontes tecnicas

### Pontos de medicao das placas

- NXP, `power_manager_test` da FRDM-MCXN947:
  https://mcuxpresso.nxp.com/mcuxsdk/latest/html/examples/_boards/frdmmcxn947/demo_apps/power_manager_test/bm/example_board_readme.html
- ST, manual `UM2407` da NUCLEO-H723ZG/MB1364:
  https://www.st.com/resource/en/user_manual/um2407-stm32h7-nucleo144-board-stmicroelectronics.pdf
- Nordic, current measurement na nRF52840-DK:
  https://docs.nordicsemi.com/r/bundle/ug_nrf52840_dk/page/ug/dk/hw_measure_current.html
- Nordic, alimentacao direta pelo conector `P21`:
  https://docs.nordicsemi.com/r/bundle/ug_nrf52840_dk/page/ug/dk/direct_supply.html
- Nordic, modo `nRF ONLY`:
  https://docs.nordicsemi.com/r/bundle/ug_nrf52840_dk/page/ug/dk/nrf_only_mode.html
- Nordic, selecao da fonte de alimentacao:
  https://docs.nordicsemi.com/r/bundle/ug_nrf52840_dk/page/ug/dk/power_source.html
- Nordic, preparo de `P22/SB40` (rota consultada e excluida por exigir corte):
  https://docs.nordicsemi.com/r/bundle/ug_nrf52840_dk/page/ug/dk/prepare_board.html

### Componentes do medidor

- TI, datasheet do `AMC3302`:
  https://www.ti.com/lit/ds/symlink/amc3302.pdf
- TI, modulo pronto `AMC3302EVM` e seu guia:
  https://www.ti.com/tool/AMC3302EVM
  https://www.ti.com/lit/ug/sbau330c/sbau330c.pdf
- TI, modulo opcional `AMC3330EVM`:
  https://www.ti.com/tool/AMC3330EVM
- Caddock, shunts PTH Kelvin Type SR:
  https://www.caddock.com/online-catalog/mrktg-lit/TypeSR.pdf
- TI, `SN74HCT14N` PDIP:
  https://www.ti.com/product/SN74HCT14/part-details/SN74HCT14N
- onsemi, `FQP30N06L` TO-220:
  https://www.onsemi.com/download/data-sheet/pdf/fqp30n06l-d.pdf
- Vishay, optoacoplador opcional `6N137` DIP:
  https://www.vishay.com/en/product/84732/
- ST, produto `NUCLEO-G474RE`:
  https://www.st.com/en/evaluation-tools/nucleo-g474re.html
- ST, datasheet do `STM32G474`:
  https://www.st.com/resource/en/datasheet/stm32g474re.pdf
- TI, upgrade opcional `ADS9224R`:
  https://www.ti.com/lit/ds/symlink/ads9224r.pdf

Os esquematicos locais das tres placas estao em `docs/hardware-pdfs/` e sao a
fonte final para conferir o adaptador da revisao fisica que sera conectada.
