# Análise das soluções de medição de corrente: Arduino Due, Nucleo e PPK2

Data: 2026-09-08.

Revisão econômica: considerada a disponibilidade de Arduino Due no Brasil
por menos de R$ 200, informada pelo usuário após a primeira análise.

Objetivo: escolher uma solução com bom compromisso entre custo, capacidade de
detectar variações de consumo e esforço de implementação nas três placas BALAS.
Esta é uma análise documental e de dimensionamento. Não houve montagem nem
ensaio físico dos medidores nesta revisão.

## 1. Parecer e recomendação

**O Arduino Due é tecnicamente válido como plataforma de aquisição de corrente.**
Com shunt, `INA180-181EVM`, aquisição por timer/PDC e constantes de calibração
incorporadas ao firmware, pode
mostrar mudanças de consumo em mA e eventos de dezenas ou centenas de
microssegundos. O `029` agora define o canal `U2/INA180A2`, faixas, filtro e
montagem PTH; ainda faltam o firmware e a caracterização física do ruído e da
banda. Não há evidência para prometer precisão em poucos µA ou pulsos de
`1–5 µs`.

**Com o Due disponível no Brasil por menos de R$ 200, ele passa a ser uma
alternativa econômica relevante mesmo comprando a placa nova.** Para priorizar
o menor desembolso, vale cotar primeiro Due + `INA180-181EVM`. A
recomendação depende do custo completo e da disposição para implementar e
calibrar o instrumento; o preço da placa não resolve sozinho essa comparação.

**O PPK2 permanece a recomendação para reduzir o tempo até obter medições**,
desde que a prioridade sejam perfis em escala de `100 µs`, milissegundos e
duração completa da inferência. Ele pode medir
hardware de outros fabricantes; não exige um MCU Nordic no dispositivo medido.
Isso está explícito na [página oficial do PPK2](https://www.nordicsemi.com/Products/Development-hardware/Power-Profiler-Kit-2).

A recomendação tem três condições que podem mudar a escolha:

- Para reconstruir o patamar de pulsos de `5 µs`, a arquitetura Nucleo + AMC3302
  dos `025–028` é mais apropriada, embora ainda precise ser validada.
- Para distinguir variações menores que `1 mA` sobre correntes acima de
  `50 mA`, o PPK2 não oferece essa resolução nominal na faixa correspondente;
  um front-end de faixa fixa merece avaliação.
- Se o isolamento galvânico dos `025–028` continuar obrigatório, nem o Due
  simplificado nem o PPK2, diretamente conectados, atendem ao mesmo requisito.
  A economia dessas alternativas envolve também uma mudança de arquitetura.

A primeira análise usava o preço do Due original na loja dos EUA e favorecia
seu uso principalmente por reaproveitamento. Esse enquadramento econômico foi
revisto: para a decisão local, a referência do Due é agora a oferta brasileira
informada. Comparar com Nucleo e PPK2 exige o preço final entregue no Brasil,
não apenas preços de catálogo em dólares. A seção 7 detalha essa distinção.

## 2. O que os documentos realmente propõem

| Documento | Conteúdo relevante | Consequência para esta decisão |
| --- | --- | --- |
| [025](025_projeto-medidor-corrente-dc-instantanea.md) | Arquitetura isolada, faixas, aquisição `BURST` e `PROFILE`, calibração | Origem dos requisitos mais exigentes de velocidade e proteção |
| [026](026_lista-compras-medidor-corrente-dc.md) | Lista de materiais da revisão modular PTH, com AMC3302EVM pronto | O custo inclui muito mais que a placa de aquisição |
| [027](027_por-que-nucleo-g474re-em-vez-de-arduino.md) | Justificativa da G474 comparada a GIGA/Portenta; modelo anterior ainda desconhecido | Não é uma comparação com o Arduino Due |
| [028](028_diagrama-montagem-medidor-corrente-pth.md) | Interligações, shunts e carga fictícia | Projeto mais detalhado, mas sem validação física |
| [029](029_projeto_medicao_corrente_arduino_due.md) | Due + canal U2/INA180A2 do INA180-181EVM + shunts e filtro PTH | Alternativa de custo com front-end montado, ainda sem validação física |

O `029` recupera a identificação do **Arduino Due**. A incerteza sobre GIGA ou
Portenta do `027` deixa de ser a base desta comparação. Também é necessário
distinguir a `NUCLEO-G474RE`, proposta como instrumento, da `NUCLEO-H723ZG`,
que é uma das placas cujo consumo será medido.

A consulta ao grafo existente confirmou a relação entre os `025–028`; como a
revisão do `029` é posterior ao grafo, as conclusões abaixo usam também a
leitura direta do documento e as fontes oficiais vinculadas no texto.

## 3. Qual desempenho é necessário para o BALAS?

O pedido atual prioriza observar variações com custo razoável. Para orientar a
escolha, adota-se como primeiro objetivo medir baseline, aumento de corrente,
duração e carga/energia da inferência. A reprodução de cada pico de poucos
microssegundos fica como requisito adicional, caso se mostre necessária.

Há evidência no próprio projeto de que a inferência completa pode durar muito
mais que um pulso de `5 µs`: o [relatório 021](021_relatorio_desempenho_stm32_vs_nxp.md)
registra historicamente `42,72 ms` para STM32/TFLM e `234,71 ms` para NXP no
modelo analisado. Esses tempos não são uma nova medição nem representam todos
os modelos atuais, mas justificam priorizar a captura de janelas longas.

| Duração de um evento | Pontos a 100 kS/s, como no PPK2 | Pontos a 500 kS/s, meta possível para o Due | Pontos a 4 MS/s, meta da G474 |
| ---: | ---: | ---: | ---: |
| 1 ms | 100 | 500 | 4.000 |
| 100 µs | 10 | 50 | 400 |
| 20 µs | 2 | 10 | 80 |
| 5 µs | 0 ou 1, conforme a fase | 2 ou 3 | 20 |

Valores calculados por `N = duração × taxa`, antes dos efeitos do filtro e do
amplificador. Ter dez pontos é um critério prático de desenho, não uma garantia
de fidelidade. Um pulso menor que o intervalo entre amostras pode aparecer
atenuado ou alargado pelo circuito analógico, ou sequer ser identificado.

Também são grandezas diferentes:

- **Resolução nominal:** quanto vale um código do conversor ou da faixa.
- **Repetibilidade:** quanto a leitura varia ao repetir a mesma condição.
- **Exatidão:** proximidade da leitura em relação à corrente de referência.
- **Resposta temporal:** quanto o instrumento preserva amplitude e duração.

Um instrumento pode detectar repetidamente uma mudança de `10 para 11 mA`
mesmo tendo erro de ganho na leitura absoluta. Em contrapartida, exibir muitas
casas decimais não prova que uma mudança de `10,00 para 10,01 mA` é real.

## 4. Validade do Arduino Due e ajustes necessários ao 029

### 4.1. O hardware de aquisição é suficiente

O SAM3X8E possui ADC de `12 bits`, até `1 MS/s`, multiplexador de entradas,
trigger por timer e transferência por PDC. O modo diferencial também existe.
São recursos adequados à arquitetura proposta. A taxa é do conversor:
alternar dois canais não produz dois canais simultâneos de `1 MS/s` cada.
[Microchip: SAM3X/SAM3A, capítulo 43](https://ww1.microchip.com/downloads/en/devicedoc/atmel-11057-32-bit-cortex-m3-microcontroller-sam3x-sam3a_datasheet.pdf).

O Due expõe 12 entradas analógicas e tem `96 KB` de SRAM de uso geral. Sua
lógica é de `3,3 V`; a interface analógica deve respeitar esse limite inclusive
na partida. [Arduino: Due](https://docs.arduino.cc/hardware/due/),
[especificações e cuidados elétricos](https://store.arduino.cc/products/arduino-due).

A API `analogRead()` retorna 10 bits por padrão; `analogReadResolution(12)`
habilita a resolução retornada de 12 bits. Isso não configura sozinho uma
aquisição rápida por PDC.
[Referência oficial Arduino](https://github.com/arduino/reference-en/blob/master/Language/Functions/Analog%20IO/analogRead.adoc).

Na caracterização dinâmica do SAM3X, a tabela 45-35 apresenta ENOB típico de
`10,0 bits` em uma classe de configurações single-ended e `11,2 bits` em outra,
sob condições específicas. Não são 12 bits úteis garantidos na placa Due.
[Datasheet, seção 45.7.2](https://ww1.microchip.com/downloads/en/devicedoc/atmel-11057-32-bit-cortex-m3-microcontroller-sam3x-sam3a_datasheet.pdf).

O ruído da montagem precisa ser medido na taxa e faixa utilizadas. ENOB é uma
medida dinâmica envolvendo ruído e distorção; não deve ser convertido diretamente
em um limite garantido de detecção de degraus DC.

### 4.2. O shunt sozinho não atende bem à sensibilidade desejada

Com referência ideal de `3,3 V`:

```text
LSB_V = 3,3 / 4096 = 805,66 µV
LSB_I = LSB_V / (Rshunt × ganho)
Vqueda = I × Rshunt
```

| Ligação sem amplificador | Queda a 10 mA | Passo ideal de corrente | Avaliação |
| --- | ---: | ---: | --- |
| Shunt de 0,1 Ω | 1 mV | 8,06 mA/código | Sensibilidade insuficiente |
| Shunt de 1 Ω | 10 mV | 0,806 mA/código | Só variações relativamente grandes |
| Shunt de 10 Ω | 100 mV | 80,6 µA/código | Mais sensível, mas interfere mais no DUT |

Em `150 mA`, o shunt de `10 Ω` retiraria `1,5 V` da alimentação. Portanto, o
exemplo de `10 mA` do `029` não pode ser generalizado para as três placas.
O [015](015_medicao-energia-placas-desenvolvimento.md) já alerta para correntes
ativas da H723 na ordem de centenas de mA em determinadas condições.

### 4.3. Front-end definido: INA180-181EVM, canal U2

O projeto revisado usa o **INA180-181EVM** completo. Essa placa traz os oito
dispositivos INA180A1–A4 e INA181A1–A4 já montados. Será usado somente o canal
`U2`, que contém o INA180A2 de ganho `50 V/V`, alimentado a `3,3 V`, com shunt
no lado positivo e saída para um único ADC do Due.

```text
Fonte + ── shunt ── alimentação do DUT
             ││
        leitura Kelvin
             ││
      INA180-181EVM U2 ── filtro PTH ── Due ── USB/PC

Fonte − ── GND do DUT ── GND do amplificador ── GND do Due
```

O EVM deve receber alimentação pelo lado da instrumentação, sem
somar seu consumo de alimentação à corrente que se pretende atribuir ao DUT.
As correntes de polarização das entradas ainda podem perturbar a medição.

O EVM não é DIP e não encaixa diretamente na protoboard. Ele fica inteiro em
uma base isolante e é ligado por mini-hooks aos pontos `TP211=VS`, `TP212=IN+`,
`TP213=IN−`, `TP214=OUT` e `TP215=GND`. Shunts, bornes e filtro de
`100 Ω + 10 nF` ficam em placas universais PTH de passo `2,54 mm`. A corrente
do DUT não passa pela protoboard nem pelos pontos de teste do EVM.
[TI: INA180-181EVM e guia SBOU183](https://www.ti.com/lit/pdf/SBOU183).

| Faixa ilustrativa | Shunt | Ganho | Limite de trabalho escolhido | Saída nesse limite | Queda no shunt | Passo ideal de corrente |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LOW | 1 Ω | 50 | 40 mA | 2,0 V | 40 mV | 16,1 µA/código |
| HIGH | 0,1 Ω | 50 | 400 mA | 2,0 V | 40 mV | 161 µA/código |

Os limites deixam margem de tensão; não tornam toda a faixa até zero igualmente
precisa. Exemplos calculados:

- LOW, de `10 para 11 mA`: a saída muda `50 mV`, aproximadamente `62 códigos`.
- LOW, de `10,0 para 10,1 mA`: muda `5 mV`, aproximadamente `6,2 códigos`.
- HIGH, de `150 para 155 mA`: muda `25 mV`, aproximadamente `31 códigos`.
- HIGH, de `150,0 para 150,1 mA`: muda apenas `0,5 mV`, menos de um código.

Isso sustenta a viabilidade para mudanças em mA. A detecção de `100 µA` na LOW
fica condicionada ao ruído e à repetibilidade; não é um desempenho já provado.

O INA180A2 tem banda típica de `210 kHz`. O datasheet diferencia offset de até
`±150 µV` com entrada em `0 V` e `±500 µV` na condição geral especificada;
neste exemplo high-side, não se deve usar o melhor número de low-side. Também
informa corrente de polarização típica de `80 µA` na condição geral e limitações
de saída perto de zero. [TI: INA180, tabela 7.5](https://www.ti.com/lit/ds/symlink/ina180.pdf).

Um offset de entrada de `500 µV` corresponde a `0,5 mA` com `1 Ω` ou `5 mA`
com `0,1 Ω`, antes de calibração. Offset estável pode ser estimado por calibração
em vários pontos; sinal cortado pela saturação perto de zero não pode ser
recuperado por subtração. Por isso esse exemplo é adequado a consumo ativo e
variações, mas não resolve medição de sleep de poucos µA.

O EVM elimina a solda do encapsulamento SMD. A montagem restante usa cabos de
teste e componentes PTH, mas ainda requer placa de shunt, filtro, fixação,
firmware e calibração. Manter o EVM inteiro evita cortar suas oito seções e
permite reaproveitar os demais canais em futuras avaliações.

### 4.4. Mudar low-side para high-side importa nas placas de desenvolvimento

O desenho inicial do `029` coloca o shunt no retorno GND. Se USB, debugger ou
outro cabo ligar o GND do DUT ao GND do computador por fora desse resistor,
parte da corrente o contorna. O instrumento pode indicar corrente menor que
a real. Além disso, o shunt eleva o GND do DUT em relação aos outros circuitos.

Nos pontos `J24` e `JP4` já documentados, o caminho interrompido é o positivo do
rail. O front-end high-side se adapta melhor a esses pontos e evita elevar o
terra do DUT. Deve-se eliminar caminhos positivos de alimentação alternativos
e back-power por GPIO. High-side mantém terra comum; não oferece isolamento.

### 4.5. Aquisição: começar com metas sustentáveis

Para o Due, a proposta de implementação é:

| Modo proposto | Taxa inicial | Banda útil pretendida do conjunto | Aplicação |
| --- | ---: | --- | --- |
| Perfil | 100 kS/s | aproximadamente 10–20 kHz | Estados e eventos de 100 µs ou mais; inferência completa |
| Captura rápida | 500 kS/s | aproximadamente 50–100 kHz | Investigar eventos de 20 µs ou mais |
| Exploração | até 1 MS/s | depende do front-end e filtro | Caracterizar o limite; sem promessa de fidelidade a 1–5 µs |

Essas são metas de projeto, não taxas medidas. O filtro anti-alias e o tempo
de aquisição do ADC precisam ser dimensionados em conjunto; somente instalar
um amplificador rápido não evita aliasing. Uma banda de `100 kHz` corresponde
a tempo de subida aproximado de `3,5 µs` em um modelo de polo único.

O firmware deve usar timer, PDC, buffers e registros de perda/overrun. O PC
deve receber blocos binários com sequência, taxa e quantidade de amostras;
o tempo é reconstruído pelo índice, não pela hora de chegada do pacote USB.
Conversão para CSV e corrente pode ocorrer posteriormente.

Com um buffer ilustrativo de `32 KiB`, usando dois bytes por amostra:

| Taxa | Janela de 16.384 amostras | Dados brutos gerados por segundo |
| ---: | ---: | ---: |
| 100 kS/s | 163,84 ms | 200 kB/s |
| 500 kS/s | 32,768 ms | 1 MB/s |
| 1 MS/s | 16,384 ms | 2 MB/s |

Logo, mesmo a `100 kS/s`, esse buffer não cobre os `234,71 ms` do exemplo NXP.
Será necessário streaming comprovado ou redução local de dados, mantendo
soma/carga, mínimo, máximo e contagem. Redução por média perde a forma dos
transientes dentro do bloco. Usar a porta USB nativa do Due para avaliar
streaming; a existência de USB não comprova a vazão contínua do firmware.

### 4.6. O Due pode substituir a G474 mantendo o AMC3302?

Pode ser investigado, mas não é troca direta de placa e firmware. O `028`
subtrai duas conversões simultâneas. Ler `OUTP` e `OUTN` sequencialmente no
Due introduz defasagem durante as bordas. O modo diferencial nativo do SAM3X
é outra possibilidade, condicionada a pares de pinos, modo comum, faixa
diferencial e configuração; um conversor diferencial para single-ended também
seria possível, com custo e erros adicionais.

Manter o AMC3302EVM preserva o item caro do front-end e parte importante da
complexidade. Não é o caminho prioritário para economizar.

### 4.7. O acesso ao Fluke resolve a calibração sem trabalho repetitivo

O acesso a um `Fluke 5500A` ou `6100A` fortalece a alternativa Due. Os dois
podem aplicar correntes DC nos intervalos usados por `LOW` e `HIGH`. O 5500A
possui faixas menores mais adequadas para caracterizar abaixo de `10 mA`; no
6100A, saídas menores que o limite inferior de `10 mA` podem ser programadas,
mas não têm exatidão especificada.

Isso não elimina a necessidade de caracterizar cada **faixa montada**, pois os
shunts são componentes físicos diferentes. Elimina a necessidade de repetir o
procedimento antes de cada ensaio: ajustar o fator efetivo de conversão para
LOW e HIGH, alterar as constantes correspondentes, recompilar e regravar o
firmware do Due. As constantes ficam na memória Flash da própria placa junto
com o programa; nenhum componente adicional de memória é necessário.

Recalibrar e gerar outro firmware somente após troca/retrabalho do hardware ou
falha em uma verificação de referência. A calibração DC corrige ganho e offset
estáveis, mas não comprova resposta temporal, ruído ou ausência de perda de
amostras.

## 5. O que o PPK2 entrega e onde ele limita

O PPK2 oferece aquisição contínua a `100 kS/s`, cinco faixas automáticas,
software de visualização/exportação e entradas digitais para correlacionar
consumo com eventos do firmware.
[Sistema de medição](https://docs.nordicsemi.com/r/bundle/ug_ppk2/page/ug/ppk/ppk_user_guide_measurement_system.html),
[produto e aplicativo](https://www.nordicsemi.com/Products/Development-hardware/Power-Profiler-Kit-2).

### 5.1. Resolução e exatidão não são constantes

| Região de corrente | Resolução típica publicada | Exatidão típica publicada para a média |
| --- | ---: | ---: |
| 0,2–50 µA | 0,2 µA | ±10% |
| 50–500 µA | 0,5 µA | ±10% |
| 0,5–5 mA | 5 µA | ±10% |
| 5–50 mA | 50 µA | ±10% |
| 50 mA–1 A | 1 mA | ±15% |

Fontes: Nordic, [resolução por faixa](https://docs.nordicsemi.com/r/bundle/ug_ppk2/page/ug/ppk/ppk_measure_resolution.html)
e [exatidão da média](https://docs.nordicsemi.com/r/bundle/ug_ppk2/page/ug/ppk/ppk_measure_accuracy.html).
Os limites acima seguem a tabela de resolução; a tabela de exatidão inicia a
primeira região em `100 nA`. A Nordic também lista offsets de `±2%` nas quatro
primeiras faixas e `±5%` na última. Não se pressupõe aqui uma base percentual
para combinar esses offsets em um único orçamento de erro.

Algum material comercial anuncia resolução mínima de `100 nA`; para esta
decisão adotou-se conservadoramente `0,2 µA` da tabela detalhada. Nenhum desses
valores se aplica a toda a faixa de corrente.

Consequências dos números publicados:

- Em `10 mA`, uma mudança de `1 mA` abrange cerca de 20 passos da faixa;
  é um caso favorável para observar diferenças, sujeito à repetibilidade.
- Em `150 mA`, uma mudança de `0,1 mA` fica abaixo da resolução nominal;
  prometer essa distinção por amostra seria incorreto.
- Autorange favorece observar sleep e atividade na mesma sessão, mas mudanças
  de faixa precisam ser consideradas ao interpretar transientes.
- Os percentuais de exatidão são para médias e não certificam amplitude de
  pulsos isolados. Repetição no mesmo equipamento pode produzir comparação
  relativa melhor, a ser demonstrada experimentalmente.

### 5.2. Limite temporal e energia

O intervalo de `10 µs` torna o PPK2 adequado para o primeiro nível de perfil
proposto. Ele não fornece dez pontos em um pulso de `10 µs`: fornece cerca de
um. A taxa de amostragem também não deve ser anunciada como largura de banda
analógica de `100 kHz`.

Em eventos curtos demais, a carga integrada pode ser menos sensível à forma
do pico que sua amplitude máxima. Ainda assim, não se garante energia correta
para um pulso arbitrário subamostrado sem avaliar a resposta do instrumento.

Com tensão suficientemente estável, calcular:

```text
Q = soma(I[k] × dt)
E_aproximada = Vrail × Q
delta_I = media(I durante atividade) − media(I em baseline)
E_incremental = Vrail × soma((I[k] − Ibaseline) × dt)
```

O valor de tensão configurado no PPK2 não substitui uma medida dinâmica
sincronizada de `Vrail(t)`. Medir a tensão antes/depois com multímetro não
detecta quedas de microssegundos. Se houver suspeita de queda transitória,
verificar com osciloscópio emprestado ou canal de tensão apropriado; até lá,
identificar a energia calculada como aproximação a tensão constante.

### 5.3. Compatibilidade elétrica e conexão nas três placas

As faixas de alimentação interna e externa do PPK2 são `0,8–5,0 V`, e a
corrente máxima de medição é `1 A`. Para source mode com demanda acima de
`400 mA`, o guia recomenda uma alimentação USB adicional capaz de fornecer
`1 A` ou mais.
[Especificações de alimentação](https://docs.nordicsemi.com/r/bundle/ug_ppk2/page/ug/ppk/ppk_power_supply_specs.html),
[alimentação do PPK2](https://docs.nordicsemi.com/r/bundle/ug_ppk2/page/ug/ppk/ppk_power_supply.html).

Mapeamento proposto a partir do [015](015_medicao-energia-placas-desenvolvimento.md),
a confirmar na revisão física de cada placa:

| Placa | Modo inicial sugerido | Caminho da corrente |
| --- | --- | --- |
| FRDM-MCXN947 | Ampere Meter | Remover jumper J24; `J24-1 → VIN PPK2`, `VOUT PPK2 → J24-2`; GND comum |
| NUCLEO-H723ZG | Ampere Meter | Remover JP4; lado `VDD → VIN PPK2`, `VOUT PPK2 → VDD_MCU`; GND comum |
| nRF52840-DK | Source Meter | `VOUT PPK2 → positivo P21`, GND comum; manter preparação e alimentação auxiliar descritas no 015 |

O princípio de conexão com `VIN`, `VOUT` e `GND` em modo amperímetro é
documentado pela [Nordic](https://docs.nordicsemi.com/r/bundle/ug_ppk2/page/ug/ppk/measure_current_ampere_meter.html).
A aplicação desse princípio a J24/JP4 é uma inferência de engenharia a partir
dos pontos de medição locais; não foi testada nesta análise.

Em modo amperímetro, a alimentação já existente da placa fornece o rail.
Em modo fonte, não colocar a saída do PPK2 em paralelo com outro regulador no
mesmo rail. Manter as conexões removíveis e, na Nordic, não cortar SB40/SB41.
Não atribuir ao MCU a corrente de toda a placa medida na entrada USB.

O PPK2 tem inserção resistiva e comutação de faixas; sua queda de tensão não
deve ser tratada como zero. A documentação consultada não forneceu um limite
único de burden aplicável a todas as condições desta bancada. Verificar a
tensão efetiva do DUT sob a maior carga e durante mudanças relevantes.

O esquema de terra comum do PPK2 não é equivalente à barreira do AMC3302.
Uma fonte inicialmente flutuante deixa de garantir isolamento do computador
quando conectada a caminhos comuns por instrumentação/USB. Se a separação
galvânica for mantida como requisito, será necessário um projeto adicional;
um isolador USB só resolveria a parte correspondente, com verificação de
alimentação, compatibilidade e todos os demais cabos.

## 6. Comparação técnica consolidada

| Critério | Due + INA180-181EVM | G474 + AMC3302EVM dos 025–028 | PPK2 |
| --- | --- | --- | --- |
| Situação | Projeto de bancada definido; firmware/ensaios pendentes | Interligação detalhada; firmware/ensaios pendentes | Instrumento comercial com aplicativo |
| Aquisição | Até 1 MS/s do ADC; iniciar em 100/500 kS/s | Meta de 4 milhões de pares simultâneos/s em BURST | 100 kS/s |
| Amplitude | 12 bits nominais; ENOB/ruído da montagem a medir | 12 bits por ADC; ruído e casamento a medir | Resolução especificada por faixa |
| Sensibilidade ideal nas faixas LOW/HIGH | 16,1 / 161 µA por código, com G=50 | 19,7 / 197 µA por passo da diferença, com G=41 | 50 µA na região de 10 mA; 1 mA na de 150 mA |
| Evento inicial de interesse | 100 µs em perfil; 20 µs em captura rápida, sujeito a teste | Patamar de 5 µs como meta de validação | Perfis de 100 µs ou mais como uso inicial |
| Sleep de poucos µA | Não atendido pelo exemplo simples | Não demonstrado nas faixas existentes | Faixas próprias para correntes pequenas |
| Isolamento do canal | Não | Sim, com interligação correta e sem caminhos que contornem a barreira | Não equivalente ao AMC3302 |
| Queda de inserção | 40 mV no limite escolhido, mais conexões | 40 mV no limite escolhido, mais conexões | Dependente da faixa e conexão; verificar |
| Registro de inferência inteira | Streaming ou redução a implementar | PROFILE com redução; BURST curto | Captura contínua pelo aplicativo |
| Esforço | Interligação PTH, aquisição, software e uma calibração inicial por faixa | Montagem modular, ADC dual, firmware, calibração | Preparação da placa e configuração do ensaio |

Os números G474/AMC combinam o projeto local com as especificações de
[STM32G474](https://www.st.com/resource/en/datasheet/stm32g474re.pdf) e
[AMC3302](https://www.ti.com/lit/ds/symlink/amc3302.pdf): ganho `41`, entrada
de `±50 mV`, banda mínima de `290 kHz` e típica de `340 kHz`.
Subtrair dois ADCs também combina seus ruídos e erros; a coluna de passo ideal
não prova superioridade metrológica sobre o PPK2.

Dois pontos do projeto Nucleo merecem atenção mesmo se ele for mantido:

1. O `BURST` de `2,048 ms` não registra uma inferência de dezenas/centenas de
   ms. O `PROFILE` previsto resolve a duração por redução de dados, com perda
   de detalhe temporal. É uma escolha diferente da série contínua do PPK2.
2. O RC de `33 Ω + 100 pF` do `028` tem frequência de corte ideal próxima de
   `48,2 MHz`. Ele é uma interface local do ADC, não um filtro anti-alias para
   perfil a `50–100 kS/s`. Para esse modo, deve-se filtrar adequadamente antes
   de amostrar ou adquirir rápido e filtrar digitalmente antes da decimação.

O conjunto Nucleo oferece vantagens reais para captura rápida e isolamento.
Essas vantagens não demonstram que ele seja o melhor investimento para o
objetivo atual de comparar perfis de consumo.

## 7. Custo com o Due comprado no Brasil por menos de R$ 200

### 7.1. Premissa brasileira para o Due

O usuário informou conseguir comprar o Arduino Due no Brasil por menos de
`R$ 200`. Adota-se `R$ 200` como teto conservador para o preço da placa neste
cenário, acrescentando frete se ele não estiver incluído. Essa informação
substitui o preço da loja oficial dos EUA como referência da compra do Due.

O link enviado é um redirecionamento publicitário do Google (`google.com/aclk`)
e não pôde ser aberto pela ferramenta de consulta. Portanto, o preço é uma
premissa fornecida pelo usuário; vendedor, revisão, procedência e frete do
anúncio específico não foram verificados. Não se presume que a placa seja
original ou compatível apenas pelo preço. As capacidades do SAM3X8E sustentam
a análise técnica, mas o ruído efetivo continua dependendo da placa recebida.

O custo do instrumento será:

```text
Custo_Due = preço_da_placa (até R$ 200 neste cenário)
          + INA180-181EVM, dois shunts e filtro PTH
          + conexões, carga de teste e montagem
          + fonte/instrumentos que ainda precisem ser comprados
          + fretes
```

Exemplos exclusivamente aritméticos para estabelecer um orçamento máximo:

| Se todos os demais itens necessários somarem… | Total usando R$ 200 para a placa |
| ---: | ---: |
| R$ 100 | R$ 300 |
| R$ 200 | R$ 400 |
| R$ 300 | R$ 500 |

Essas linhas **não são cotações de front-end nem promessas de montagem por
esse valor**. Mostram quanto sobra para o circuito e acessórios em cada
orçamento. Se forem necessários uma fonte nova ou montagem terceirizada,
esses valores também devem entrar na coluna dos demais itens.

O preço brasileiro muda a conclusão: o Due não precisa estar disponível no
laboratório para merecer consideração. Pode justificar a compra para um
medidor simples, desde que os demais itens mantenham a economia e que o
desempenho seja aprovado nos ensaios da seção 8.

### 7.2. Referências internacionais e projeto com AMC3302

Preços unitários exibidos nas páginas consultadas em 2026-09-08. Valores em
USD, sem conversão para reais, frete, tributos de importação ou fechamento de
carrinho brasileiro. São referências de catálogo, não orçamento entregue. O
preço do INA180-181EVM foi consultado nesta revisão; os demais vieram da
primeira análise.

| Item | Preço exibido | Fonte comercial |
| --- | ---: | --- |
| NUCLEO-G474RE | US$ 20,13 | [DigiKey](https://www.digikey.com/en/products/detail/stmicroelectronics/NUCLEO-G474RE/10231585) |
| AMC3302EVM | US$ 67,38 | [DigiKey](https://www.digikey.com/en/products/detail/texas-instruments/AMC3302EVM/15222321) |
| Arduino Due original com headers, apenas como referência internacional | US$ 49,40 | [Arduino Store EUA](https://store-usa.arduino.cc/products/arduino-due) |
| INA180-181EVM | US$ 13,75 | [Mouser](https://www.mouser.com/ProductDetail/Texas-Instruments/INA180-181EVM) |
| NRF-PPK2 | US$ 107,30 | [DigiKey](https://www.digikey.com/en/products/detail/nordic-semiconductor-asa/NRF-PPK2/13557476) |

```text
G474 + AMC3302EVM = US$ 87,51
Diferença para o PPK2 = US$ 19,79
Due original + INA180-181EVM = US$ 63,15
Diferença para o PPK2 = US$ 44,15
```

Apenas `US$ 19,79` separam os dois módulos principais do projeto Nucleo do
PPK2 completo. Já Due original + INA180-181EVM ficam `US$ 44,15` abaixo do
PPK2 nessa referência internacional, antes de shunts, conectores, carga,
montagem e desenvolvimento. A oferta brasileira abaixo de R$ 200 pode aumentar
a vantagem do Due, mas a comparação final depende do EVM entregue no Brasil.

### 7.3. Comparar custos completos na mesma moeda

| Alternativa | Como calcular o desembolso completo |
| --- | --- |
| G474 + AMC | US$ 87,51 + shunts/Kelvin + shield/filtros + carga de teste + montagem + fonte disponível ou comprada + cabos |
| Due já disponível | INA180-181EVM + shunts/filtro PTH + montagem + carga de teste + fonte disponível ou comprada + cabos |
| Due novo comprado no Brasil | Até R$ 200 pela placa, conforme informado, + todos os itens da linha anterior |
| PPK2 | US$ 107,30 + USB/chicotes necessários + fonte externa ou auxiliar quando exigida pela conexão |

Computador e instrumento de referência devem ser considerados conforme o que
o laboratório já possui. Software de aquisição e horas de depuração também
têm custo, mesmo quando não há pagamento adicional. Os preços em USD da tabela
precisam ser substituídos por cotações finais em BRL antes de comparar o
desembolso. Não se aplica aqui uma conversão cambial arbitrária nem uma
estimativa não verificada do PPK2 entregue no Brasil.

O `029` agora seleciona o `INA180-181EVM`, mas esta análise não obteve uma
cotação brasileira completa do EVM, shunts e acessórios. Portanto, ainda não
há base para afirmar um total fechado do Due ou um percentual garantido de
economia.

Uma regra de decisão proposta, e não especificação de fabricante: investir
no protótipo se o **custo completo do Due**, incluindo a placa quando nova,
ficar em até aproximadamente metade do PPK2 entregue e o desenvolvimento
tiver utilidade para o projeto. Essa margem remunera o esforço adicional e
o risco de retrabalho; não é um limite técnico. Se a diferença de custo for
pequena, o PPK2 favorece o tempo até obter resultados.

Há ainda uma alternativa conceitual útil: o mesmo INA180-181EVM de saída única
poderia ser conectado a uma G474 usando apenas um ADC. A simplificação
vem da troca do front-end isolado e dos requisitos, não do nome Arduino.
O catálogo internacional favorecia a Nucleo frente ao Due original da loja
oficial, mas isso não determina qual placa chega mais barata ao usuário no
Brasil. Usar cotação local equivalente para essa comparação. A opção G474
simplificada também exige projeto e calibração.

## 8. Validação proporcional ao objetivo

Para decidir se uma solução detecta variações úteis, proponho estas metas
iniciais. São critérios do experimento, não desempenho já medido:

| Ensaio | Objetivo inicial |
| --- | --- |
| Corrente de referência | Com o Fluke, ajustar LOW em 10/20/30/40 mA e HIGH em 50/100/200/300/400 mA; no 5500A, acrescentar 2/5 mA se necessário |
| Variação em consumo baixo | Distinguir repetidamente 10 de 11 mA; depois tentar 10,0 de 10,1 mA |
| Variação em consumo alto | Distinguir repetidamente 150 de 155 mA |
| Duração | Capturar degraus de 1 ms e 100 µs; testar 20 µs apenas se necessário |
| Dados | Nenhum bloco perdido ou saturação no ensaio aceito |
| DUT | Tensão dentro da faixa prevista, sem alteração de comportamento atribuível à inserção |

Começar com cargas conhecidas e comutadas, antes das placas BALAS. Verificar
o degrau efetivo, pois corrente de resistor depende da tensão real e do shunt.
Para amplitude/tempo de pulsos rápidos, um multímetro não é referência
suficiente: usar equipamento temporal de referência, quando disponível.

Na faixa escolhida, repetir baseline e atividade pelo menos 20 vezes, mantendo
a mesma tensão, cabos, taxa, filtro e janela. Registrar média, dispersão e
diferença entre condições. Como regra operacional inicial:

```text
delta_I observado > 5 × desvio padrão da medida em condição constante
```

O desvio deve corresponder à mesma grandeza comparada: amostras individuais
para picos, médias de janelas para médias. Esse critério não elimina erro
sistemático, deriva ou autorange; deve ser acompanhado da calibração e da
checagem de falsos eventos. Não supor que milhares de amostras filtradas sejam
estatisticamente independentes.

No BALAS, usar execução autônoma, tensor pré-carregado e uma janela definida
em torno da inferência. Marcador GPIO pode facilitar a correlação; preservar
ou avaliar o isolamento conforme a arquitetura. Evitar comunicação de dados
durante a janela quando ela altera o consumo do rail observado.

Registrar placa/revisão, ponto de inserção, firmware/modelo, tensão, faixa,
taxa, filtro, baseline, calibração e eventuais perdas. Manter a distinção do
`015`: NXP/ST em rail dedicado e Nordic por alimentação externa do SoC.
Capacitores locais também alteram o perfil visto no shunt; o sinal representa
o rail escolhido, não cada pulso interno da CPU.

## 9. Decisão proposta para continuidade

1. **Para priorizar custo, cotar o conjunto com Due nacional por até R$ 200**,
   mesmo que a placa ainda precise ser comprada. Começar com uma faixa
   adequada ao pico real e o `INA180-181EVM`. Fechar os custos restantes e
   aprovar o desempenho pelos degraus conhecidos, antes de investir em
   múltiplas faixas.
2. **Para priorizar rapidez e menor esforço de implementação, escolher o
   PPK2** para consumo ativo, baseline e energia aproximada por inferência,
   aceitando seus limites de resolução e terra comum. Comparar seu custo
   entregue com o conjunto completo do Due, em BRL.
3. **Retomar o medidor G474 + AMC3302 quando houver necessidade demonstrada de
   pulsos de 5 µs ou isolamento galvânico**. A compra dos itens do `026` não é
   o próximo passo recomendado apenas para obter o primeiro perfil de consumo.

O `029` agora define o circuito analógico com o canal U2 do INA180-181EVM, mas
precisa ser montado, programado, calibrado e ensaiado. Para o objetivo atual, o principal ganho do
PPK2 é reunir aquisição, autorange e software prontos com custo próximo ao
conjunto modular. Com a oferta brasileira informada, a opção Due também vale
pelo baixo custo da placa nova e pela faixa fixa personalizável; a opção
G474/AMC vale pela captura rápida e pela barreira galvânica. O preço local
fortalece o Due economicamente, sem alterar seus limites de medição. A escolha
deve seguir a menor variação e a menor duração que o experimento realmente
precisa distinguir.
