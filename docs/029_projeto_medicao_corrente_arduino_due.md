# Projeto de medição de corrente DC com Arduino Due e INA180-181EVM

Revisão: 2026-09-08.

Status: arquitetura de bancada definida para montagem com módulos prontos e
componentes PTH. O hardware e o firmware ainda não foram montados nem validados.
Validar com carga conhecida antes de conectar qualquer placa BALAS.

## 1. Objetivo e escopo

Esta revisão usa:

- Arduino Due como plataforma de aquisição;
- placa de avaliação `INA180-181EVM` da Texas Instruments como front-end já
  montado;
- canal `INA180A2`, de ganho fixo `50 V/V`, presente no EVM;
- duas placas de shunt Kelvin PTH, `1 Ω` e `0,1 Ω`;
- uma placa universal PTH de passo `2,54 mm` para filtro, bornes e conexões.

O objetivo inicial é registrar a forma temporal do consumo ativo das placas
BALAS, detectar variações em mA e calcular corrente média e carga/energia
aproximada durante a inferência. Medir correntes de sleep de poucos µA ou
reproduzir pulsos de `1–5 µs` não faz parte da primeira versão.

A comparação com a solução Nucleo + AMC3302EVM e com o PPK2 está no
[documento 030](030_analise_medicao_corrente_due_nucleo_ppk2.md).

## 2. Decisão sobre a montagem

O `INA180-181EVM` resolve a montagem SMD do amplificador. O kit contém uma PCB
com oito circuitos populados: INA180A1–A4 e INA181A1–A4. Nesta revisão será
usado somente o circuito `U2`, que contém o `INA180A2` com ganho `50 V/V`.

O EVM **não é um componente DIP** e não encaixa diretamente em uma protoboard.
Ele expõe os sinais em pequenos pontos de teste SMD. A montagem adotada é:

1. manter o EVM inteiro, sem cortar suas oito seções;
2. fixá-lo em base isolante com espaçadores;
3. ligar seus pontos de teste com cabos mini-hook;
4. terminar esses cabos em bornes ou pinos de uma placa universal PTH;
5. montar shunt e filtro somente com componentes PTH.

Não é necessário soldar no EVM. Uma protoboard sem solda pode ser usada para
validar a saída em baixa energia, mas não deve conduzir a corrente do DUT nem
ser a montagem final do shunt. Para as medições, usar placa universal FR-4
ilhada, passo `2,54 mm`, com bornes plugáveis.

## 3. Arquitetura

```mermaid
flowchart LR
    PSU["Fonte ou rail existente"]
    SH["Shunt Kelvin PTH<br/>1 ohm ou 0,1 ohm"]
    DUT["Placa BALAS"]
    EVM["INA180-181EVM<br/>U2 / INA180A2 / ganho 50"]
    FILT["Placa PTH<br/>100 ohm + 10 nF"]
    DUE["Arduino Due<br/>A0 / ADC 12 bits / PDC"]
    PC["PC<br/>dados binários e análise"]

    PSU -->|corrente do DUT| SH --> DUT
    SH -. "sense Kelvin" .-> EVM
    EVM -->|OUT| FILT --> DUE --> PC
```

O shunt fica no lado positivo da alimentação. O caminho de potência e os fios
de sense são separados. O EVM e o Due compartilham GND com o DUT; esta solução
não oferece isolamento galvânico.

## 4. Canal selecionado do INA180-181EVM

A documentação oficial identifica o circuito `U2` como `INA180A2`, ganho 50.
Usar apenas os pontos de teste populados terminados em `11` a `15`:

| Ponto no EVM | Sinal | Ligação desta revisão |
| --- | --- | --- |
| `TP211` | `VS` | `3V3` do Arduino Due |
| `TP212` | `IN+` | sense Kelvin do lado da fonte do shunt |
| `TP213` | `IN−` | sense Kelvin do lado do DUT |
| `TP214` | `OUT` | entrada do filtro PTH e depois `A0` do Due |
| `TP215` | `GND` | GND do Due e do DUT |

Não usar os circuitos `U1`, `U3`–`U8` na primeira versão e não unir suas
alimentações. O layout também oferece `TP201`–`TP205` como pontos alternativos
de passagem. Eles exigiriam terminais adequadamente soldados para uma conexão
mecânica confiável e, por isso, não são usados nesta montagem sem solda no EVM.
Os mini-hooks prendem nos pontos Keystone `TP211`–`TP215` já populados.

O EVM não possui o shunt da aplicação. `TP212` e `TP213` recebem apenas os fios
Kelvin e não devem conduzir a corrente da placa. A corrente passa pelos
terminais de corrente do shunt PTH.

Segundo a TI, o INA180 opera com alimentação de `2,7–5,5 V`, aceita modo comum
de `−0,2 a 26 V` e o A2 tem ganho fixo de `50 V/V`. Alimentar o canal com
`3,3 V` garante que a saída nominal permaneça compatível com o ADC do Due,
desde que a saturação seja evitada.

## 5. Faixas de corrente

Usar duas placas fisicamente separadas. Não usar chave de faixa no caminho de
corrente da primeira versão.

| Faixa | Shunt | Limite operacional inicial | Saída no limite | Queda no shunt | Passo ideal do ADC |
| --- | ---: | ---: | ---: | ---: | ---: |
| `LOW` | `1,000 Ω` | `40 mA` | `2,0 V` | `40 mV` | `16,1 µA/código` |
| `HIGH` | `0,100 Ω` | `400 mA` | `2,0 V` | `40 mV` | `161 µA/código` |

Cálculos com ADC ideal de 12 bits e referência de `3,3 V`:

```text
Vout = I × Rshunt × 50
I = Vout / (Rshunt × 50)
LSB = 3,3 V / 4096 = 805,66 µV
```

Os limites de `2,0 V` deixam margem para ruído e transientes. A TI recomenda
manter a saída do EVM aproximadamente entre `10 mV` acima do GND e `100 mV`
abaixo da alimentação. Consequentemente, a região linear inferior nominal
começa perto de:

```text
LOW:  10 mV / (50 × 1 Ω)   = 0,2 mA
HIGH: 10 mV / (50 × 0,1 Ω) = 2 mA
```

Offset, ruído e ADC elevam o limite prático. Esta configuração não substitui o
PPK2 para correntes de sleep em µA.

### 5.1. Variações que justificam a prova de conceito

Valores ideais, antes de ruído e calibração:

| Evento | Mudança na saída | Mudança no ADC |
| --- | ---: | ---: |
| LOW: `10 → 11 mA` | `50 mV` | aproximadamente 62 códigos |
| LOW: `10,0 → 10,1 mA` | `5 mV` | aproximadamente 6 códigos |
| HIGH: `150 → 155 mA` | `25 mV` | aproximadamente 31 códigos |
| HIGH: `150,0 → 150,1 mA` | `0,5 mV` | menos de 1 código |

O primeiro critério é distinguir repetidamente mudanças de `1 mA` em torno de
`10 mA` e de `5 mA` em torno de `150 mA`. Detectar `100 µA` na faixa LOW será
um resultado experimental, não uma especificação antecipada.

## 6. Placa PTH do shunt

Montar uma placa LOW e outra HIGH. Cada uma usa um shunt de quatro terminais:

```text
        caminho de corrente

RAIL_IN o────── C  RSHUNT  C ──────o RAIL_OUT
                  S       S
                  │       │
                  │       └───────── SENSE_DUT  -> TP213
                  └───────────────── SENSE_FONTE -> TP212

C = terminal de corrente
S = terminal Kelvin
```

Componentes recomendados:

- Caddock `SR10-1.00-1%`, `1 Ω`, 1 W, quatro terminais, para LOW;
- Caddock `SR10-0.10-1%`, `0,1 Ω`, 1 W, quatro terminais, para HIGH;
- borne plugável de duas vias para `RAIL_IN/RAIL_OUT`;
- borne plugável de duas vias para `SENSE_FONTE/SENSE_DUT`;
- fio AWG 22 no caminho de corrente;
- par trançado AWG 24 ou 26 nos fios de sense.

Não passar `RAIL_IN` ou `RAIL_OUT` pela protoboard sem solda, por cabo
mini-hook ou por jumper Dupont. Esses recursos ficam restritos a alimentação e
sinais de baixa corrente do EVM.

## 7. Placa PTH de interface com o Due

Montar em placa universal de passo `2,54 mm`:

```text
EVM TP214 OUT ── R1 100 Ω ──+── Arduino Due A0
                             |
                           C1 10 nF
                             |
EVM TP215 GND ───────────────+── Arduino Due GND

Arduino Due 3V3 ───────────────── EVM TP211 VS
```

Usar `C1` C0G/NP0 se disponível. O polo ideal de `100 Ω + 10 nF` é:

```text
fc = 1 / (2 × pi × 100 Ω × 10 nF) = 159 kHz
```

O resistor também separa o capacitor e a entrada amostrada do ADC da saída do
amplificador. A banda típica do INA180A2 é `210 kHz`; os dois efeitos combinados
devem ser medidos. A ordem de grandeza esperada atende degraus de `20 µs` ou
mais, mas não garante a reprodução de pulsos de `5 µs`.

Colocar R1 e C1 próximos ao pino A0. Levar `TP214`, `TP215` e `TP211` por cabos
curtos. Manter o par de sense separado da USB e de sinais digitais rápidos.

A lista de aquisição e a mensagem administrativa ao orientador ficam em
arquivo local não versionado, fora da numeração dos documentos do projeto.

## 8. Aquisição no Arduino Due

O SAM3X8E oferece ADC de 12 bits, conversão até `1 MS/s`, trigger por timer e
PDC. A API `analogRead()` não atende sozinha à captura de alta velocidade.

Implementar inicialmente:

| Modo | Aquisição interna | Saída desejada | Uso |
| --- | ---: | ---: | --- |
| `PROFILE` | `500 kS/s` | `50 ou 100 kS/s` após filtragem/decimação | inferência completa, baseline e energia |
| `BURST` | `500 kS/s` | amostras brutas | degraus de `20 µs` ou mais |
| `LIMIT` | até `1 MS/s` | amostras brutas | caracterização, somente após PROFILE/BURST estáveis |

A taxa de `500 kS/s` é meta de firmware, não resultado medido. O modo PROFILE
deve filtrar digitalmente antes de decimar; selecionar uma amostra em cada
grupo sem filtragem produz aliasing.

Usar timer, ADC, PDC e buffers duplos. Registrar contador de buffers e condição
de overrun. Transmitir blocos binários e converter para CSV no PC. O timestamp
de cada amostra deriva do índice e da taxa configurada, não do instante em que
o pacote USB chegou.

Com buffer de `32 KiB` e amostras de 16 bits:

| Taxa | Janela no buffer | Dados brutos por segundo |
| ---: | ---: | ---: |
| 100 kS/s | `163,84 ms` | `200 kB/s` |
| 500 kS/s | `32,768 ms` | `1 MB/s` |
| 1 MS/s | `16,384 ms` | `2 MB/s` |

Uma inferência mais longa requer streaming sem perdas ou estatísticas locais.
Não emitir `Serial.print()` de texto dentro da janela medida.

## 9. Calibração inicial e constantes no firmware

Não é necessário recalibrar antes de cada medição. É necessário fazer uma
calibração inicial do **conjunto montado de cada faixa**, porque a tolerância
do shunt, o ganho real do INA180A2, a referência/ganho do ADC e as conexões
Kelvin contribuem para o fator final. Trocar apenas o valor nominal na equação
não corrige essas diferenças.

O ganho de `50 V/V` do INA180A2 é fixo no hardware. O valor alterado no
firmware é o **fator de conversão efetivo** da cadeia completa. Ajustar uma reta
para cada faixa:

```text
I_calibrada = (codigo_ADC_medio - offset_ADC_faixa) × ampere_por_codigo_faixa
```

`ampere_por_codigo_faixa` corrige o ganho efetivo formado pelo shunt, INA180 e
ADC. `offset_ADC_faixa` pode ser mantido se o ensaio mostrar offset mensurável;
o ponto de corrente zero é diagnóstico e a reta não deve ser forçada a passar
pela origem. Não adicionar potenciômetro ao caminho analógico.

### 9.1. Uso do Fluke 5500A ou 6100A

Os dois instrumentos podem fornecer corrente DC suficiente. O `5500A` possui
faixas DC desde `3,29999 mA` até `11 A`; o `6100A` possui faixa de corrente
iniciando em `10 mA`. No `6100A`, valores menores que o mínimo da faixa podem
ser programados, mas não têm exatidão especificada. Assim, usar:

| Faixa do medidor | Pontos DC recomendados |
| --- | --- |
| `LOW / 1 Ω` | `10, 20, 30 e 40 mA`; com o 5500A, acrescentar `2 e 5 mA` se essa região for relevante |
| `HIGH / 0,1 Ω` | `50, 100, 200, 300 e 400 mA` |

Para calibrar, retirar o DUT e fechar somente o laço de corrente:

```text
Fluke I HI -> terminal de corrente RAIL_IN do shunt
RAIL_OUT do shunt -> Fluke I LO

SENSE_FONTE -> INA180 IN+
SENSE_DUT   -> INA180 IN-
INA180 OUT  -> filtro -> Due A0
Fluke I LO  -> GND do EVM/Due para definir o modo comum
```

Começar com o Fluke em `STANDBY`, conferir a polaridade e programar o menor
ponto antes de ativar a saída. A queda máxima prevista é `40 mV`, muito abaixo
da compliance dos dois calibradores. A ligação de `LO`, guard e terra deve ser
confirmada pelo responsável do laboratório conforme o manual e a configuração
do equipamento disponível.

Essa calibração DC corrige amplitude estática. Ela não caracteriza banda,
tempo de subida nem perdas de buffer; a resposta temporal continua exigindo
ensaio com degraus conhecidos.

### 9.2. Incorporação do ajuste ao firmware

Depois de obter os coeficientes com o Fluke, atualizar constantes no código:

```cpp
constexpr float CURRENT_PER_COUNT_LOW_A  = /* valor calibrado */;
constexpr float CURRENT_PER_COUNT_HIGH_A  = /* valor calibrado */;
```

Essas duas constantes de ganho são o procedimento mínimo. Adicionar constantes
de offset somente se a validação mostrar erro relevante para a grandeza que
será comparada; para diferenças entre execuções, um offset estável se cancela.

Em seguida, recompilar e regravar o firmware do Due pela USB. As constantes
ficam armazenadas junto com o programa na memória Flash da própria placa e
permanecem após desligar. Não é necessário adicionar qualquer componente de
memória.

Manter no PC um pequeno relatório com identificador `LOW-01`/`HIGH-01`, pontos
aplicados, constantes obtidas, resíduos do ajuste, data e identificação do
calibrador. Esse arquivo fornece rastreabilidade; não participa da medição.

A calibração permanece válida entre campanhas. Recalibrar e regravar somente
se houver troca do resistor/placa de shunt, retrabalho nos terminais Kelvin,
troca do Due ou EVM, alteração do caminho analógico/filtro ou falha em uma
checagem de referência.

### 9.3. Critérios de aceitação

Critérios iniciais, propostos para o projeto:

1. nenhuma saturação e nenhum buffer perdido;
2. tensão do DUT permanece dentro do limite definido para a placa;
3. erro da média menor ou igual a `5%` nos pontos de calibração;
4. distinguir `10 mA` de `11 mA` em 20 repetições na faixa LOW;
5. distinguir `150 mA` de `155 mA` em 20 repetições na faixa HIGH;
6. detectar degraus de `1 ms`, `100 µs` e `20 µs`, nessa ordem;
7. diferença medida entre estados maior que cinco desvios-padrão do baseline
   calculado para a mesma grandeza e janela.

Separar erro absoluto de repetibilidade. A calibração pode reduzir ganho e
offset estáveis; não recupera sinal saturado nem elimina deriva ou ruído.

## 10. Conexão às placas BALAS

Usar os pontos removíveis documentados no
[documento 015](015_medicao-energia-placas-desenvolvimento.md):

| Placa | Ponto | Faixa inicial | Observação |
| --- | --- | --- | --- |
| FRDM-MCXN947 | `J24 / IDD_MCU` | HIGH | remover o jumper; fonte em `J24-1`, DUT em `J24-2` |
| NUCLEO-H723ZG | `JP4 / IDD` | HIGH | remover o jumper; lado VDD como fonte e VDD_MCU como DUT |
| nRF52840-DK | `P21` | LOW após confirmar pico | manter `SW9=VDD`, `SW10=ON` e `SW6=nRF ONLY` |

Antes de usar LOW, confirmar pela faixa HIGH que o pico fica abaixo de `40 mA`.
Eliminar alimentações positivas paralelas e back-power por GPIO. GND comum é
necessário nesta arquitetura, mas cabos adicionais podem formar laços de terra.
Nenhuma placa BALAS deve ser soldada, cortada ou ter ponte alterada.

## 11. Limites da solução

- Não há isolamento galvânico entre DUT, EVM, Due e computador.
- O EVM é uma plataforma de avaliação, não uma placa DIP nem um instrumento
  calibrado.
- A montagem não cobre sleep de poucos µA.
- A faixa precisa ser trocada com tudo desligado.
- O ADC do Due, sua referência, cabos e montagem determinam o ruído real.
- A banda e as taxas sustentadas precisam ser medidas.
- O EVM completo ocupa mais espaço que um pequeno módulo dedicado.
- Os sete circuitos não usados não melhoram automaticamente a medição.
- A calibração DC com o Fluke não comprova a resposta temporal do sistema.

## 12. Fontes técnicas

- TI, [INA180-181EVM](https://www.ti.com/tool/INA180-181EVM) e
  [guia SBOU183](https://www.ti.com/lit/pdf/SBOU183): conteúdo do kit,
  canais U1–U8, pontos de teste, alimentação e uso com shunt externo;
- TI, [datasheet INA180](https://www.ti.com/lit/ds/symlink/ina180.pdf): ganho,
  banda, offset, modo comum e limites de saída;
- Microchip,
  [datasheet SAM3X/SAM3A](https://ww1.microchip.com/downloads/en/devicedoc/atmel-11057-32-bit-cortex-m3-microcontroller-sam3x-sam3a_datasheet.pdf):
  ADC de 12 bits, `1 MS/s`, timer e PDC;
- Arduino, [Arduino Due](https://docs.arduino.cc/hardware/due/): tensão de
  `3,3 V`, entradas analógicas, USB e memória;
- Caddock, [Type SR Current Sense](https://www.caddock.com/online-catalog/mrktg-lit/TypeSR.pdf):
  shunts PTH de quatro terminais.
- Fluke, [manual do 5500A](https://assets.fluke.com/manuals/5500a___omeng1100.pdf):
  faixas, incerteza e compliance da saída de corrente DC;
- Fluke, [manual do 6100A](https://assets.fluke.com/manuals/6100a___umeng0500.pdf):
  faixas e especificações de corrente DC;
- Arduino, [especificações do Due](https://store.arduino.cc/products/arduino-due):
  memória Flash/SRAM e limites de `3,3 V`.
