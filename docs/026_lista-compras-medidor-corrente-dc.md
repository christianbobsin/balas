# Lista de compras do medidor de corrente DC modular PTH

Revisao: 2026-09-03

Status: lista para cotacao da revisao de laboratorio. O circuito usa modulos
prontos e componentes PTH em placas padronizadas. O hardware ainda nao foi
montado nem validado; a compra nao autoriza ligacao imediata nas placas BALAS.

O circuito e a pinagem estao em
[028_diagrama-montagem-medidor-corrente-pth.md](028_diagrama-montagem-medidor-corrente-pth.md).
A justificativa da placa de aquisicao esta em
[027_por-que-nucleo-g474re-em-vez-de-arduino.md](027_por-que-nucleo-g474re-em-vez-de-arduino.md).

## 1. O que mudou na lista

A proposta anterior exigia uma PCBA personalizada com varios componentes SMD.
Ela foi substituida na primeira versao por:

- um `AMC3302EVM` pronto, que concentra o amplificador SMD, o conversor DC/DC,
  o isolamento, o filtro e os bornes;
- um shield no padrao mecanico Arduino Uno R3 sobre a `NUCLEO-G474RE`;
- placas universais ilhadas de passo `2,54 mm`;
- shunts de quatro terminais e demais componentes PTH.

Assim, nao e necessario contratar montagem SMD nem fabricar PCB personalizada.
O canal de tensao dinamica e o optoacoplador do marcador ficam opcionais para a
segunda etapa.

Precos e estoque variam. Os links foram conferidos em 2026-09-03; confirmar
MPN, encapsulamento e prazo no carrinho. Preferir DigiKey/Mouser ou outro
distribuidor autorizado para os componentes criticos.

## 2. Compra obrigatoria da primeira etapa

| Qtd. | Item exato ou requisito | Tipo | Onde comprar | Uso |
| ---: | --- | --- | --- | --- |
| 1 | `NUCLEO-G474RE` original ST | placa pronta | [DigiKey Brasil](https://www.digikey.com.br/en/products/detail/stmicroelectronics/NUCLEO-G474RE/10231585), [Mouser Brasil](https://br.mouser.com/new/stmicroelectronics/stm-nucleo-g474re-board/) ou [ST](https://www.st.com/en/evaluation-tools/nucleo-g474re.html) | dois ADCs simultaneos, timer, DMA e USB |
| 1 | Texas Instruments `AMC3302EVM` | placa pronta com bornes | [DigiKey Brasil](https://www.digikey.com.br/en/products/detail/texas-instruments/AMC3302EVM/15222321), [TI](https://www.ti.com/tool/AMC3302EVM) ou Mouser pelo MPN | amplificacao e isolamento do shunt |
| 1 | proto-shield R3, grade `2,54 mm`, headers empilhaveis | placa padrao PTH | [Adafruit Proto Shield](https://www.adafruit.com/product/2077), [Proto-ScrewShield PTH](https://www.adafruit.com/product/196) ou equivalente local | interface PTH com `A0`, `A1`, `5V` e `GND` |
| 3 | placa universal ilhada FR-4, `5 x 7 cm`, passo `2,54 mm` | placa padrao PTH | loja local de eletronica, FilipeFlop, UsinaInfo, Mercado Livre ou distribuidor | shunts, carga e uma reserva |
| 1 | Caddock `SR10-0.10-1%` | shunt PTH, quatro terminais, `0,1 ohm`, `1 W` | [DigiKey](https://www.digikey.com.br/pt/products?keywords=SR10-0.10-1%25), Mouser `684-SR10-0.10` ou distribuidor Caddock | faixa HIGH |
| 1 | Caddock `SR10-1.00-1%` | shunt PTH, quatro terminais, `1 ohm`, `1 W` | [DigiKey](https://www.digikey.com/en/products/detail/caddock-electronics-inc/SR10-1-00-1/2182100), Mouser `684-SR10-1.00` ou distribuidor Caddock | faixa LOW |
| 2 | `33 ohm`, `1%`, `0,25 W` | resistor axial PTH | loja local, DigiKey ou Mouser | serie com `A0/A1` |
| 2 | `100 pF`, C0G/NP0, `50 V` | capacitor radial PTH | loja local, DigiKey ou Mouser | filtro junto a `A0/A1` |
| 4 | borne PTH plugavel, passo `5,08 mm`, duas vias, macho + plug | conector PTH | loja local, DigiKey, Mouser, FilipeFlop ou UsinaInfo | potencia, sense e alimentacao do EVM |
| 1 | borne PTH plugavel, passo `5,08 mm`, tres vias, macho + plug | conector PTH | mesmos fornecedores | `OUTP`, `OUTN`, `GND_MEDIDOR` |
| 1 | fio flexivel `AWG 22`, vermelho/laranja/preto | fio de potencia | loja de eletronica | caminho da corrente |
| 1 | cabo de par trancado `AWG 24` ou `AWG 26` | fio de sinal | loja de eletronica ou cabo de rede Cat5e reaproveitado e identificado | Kelvin e saidas analogicas |
| 1 | kit de espacadores e parafusos de nylon M3 | mecanica isolante | loja de componentes, robotica ou impressao 3D | fixar EVM e placas numa base isolante |
| 1 | cabo USB de dados compativel com a revisao da NUCLEO | pronto | loja de informatica | alimentacao e exportacao |
| 1 | multimetro digital | instrumento | loja de instrumentos | continuidade, tensao e calibracao |
| 1 | fonte de bancada com `3,3 V`, limite de corrente ajustavel e OVP/OCP | instrumento | revendedor de instrumentos | carga ficticia e alimentacao controlada do DUT |

Comprar uma placa universal extra e pelo menos dois bornes extras reduz o risco
de parar a montagem por dano mecanico. Nao substituir os shunts por resistores
comuns de fio enrolado: a indutancia e a ausencia de terminais Kelvin pioram a
resposta e a repetibilidade.

## 3. Componentes PTH da carga ficticia

| Qtd. | Item | Encapsulamento/requisito | Onde comprar |
| ---: | --- | --- | --- |
| 1 | `SN74HCT14N` | `PDIP-14`, ativo, seis inversores Schmitt, alimentacao `5 V` | [TI](https://www.ti.com/product/SN74HCT14/part-details/SN74HCT14N), DigiKey ou Mouser pelo MPN |
| 1 | soquete torneado `DIP-14`, passo `2,54 mm` | PTH | loja local, DigiKey ou Mouser |
| 2 | onsemi `FQP30N06L` | MOSFET canal N, `TO-220`, caracterizado com `VGS = 5 V` | [datasheet onsemi](https://www.onsemi.com/download/data-sheet/pdf/fqp30n06l-d.pdf), DigiKey ou Mouser pelo MPN |
| 1 | `330 ohm`, `1%`, `0,25 W` | axial PTH | loja local |
| 1 | `120 ohm`, `1%`, `0,5 W` | axial PTH | loja local |
| 1 | `22 ohm`, `1%`, `2 W` | axial PTH, metal film/metal oxide, nao indutivo se disponivel | loja local, DigiKey ou Mouser |
| 2 | `100 ohm`, `1%`, `0,25 W` | axial PTH, resistor de gate | loja local |
| 2 | `100 kohm`, `1%`, `0,25 W` | axial PTH, pull-down de gate | loja local |
| 1 | `100 nF`, ceramico, `50 V` | radial PTH | loja local |
| 3 | borne PTH plugavel de duas vias, `5,08 mm` | macho + plug | loja local ou distribuidor |
| 4 | ponto de teste em laco | PTH | loja local, DigiKey ou Mouser |

O soquete DIP e recomendado: permite trocar o `SN74HCT14N` sem dessoldar o CI.
Os MOSFETs ficam de pe, com pelo menos `5 mm` entre os corpos e sem dissipador;
as correntes do teste sao baixas. Confirmar no datasheet a sequencia
`G-D-S` antes de soldar, sem confiar apenas na posicao visual.

## 4. Ferramentas de montagem

| Qtd. | Item | Observacao |
| ---: | --- | --- |
| 1 | ferro de solda com controle de temperatura, ponta fina/media | `320 a 350 °C` como ponto inicial para solda com chumbo; ajustar ao material |
| 1 | suporte e esponja/limalha de latao | seguranca e limpeza da ponta |
| 1 | solda fina e fluxo no-clean | conforme regra do laboratorio |
| 1 | sugador ou malha dessoldadora | correcoes PTH |
| 1 | alicate de corte e decapador | fios e terminais |
| 1 | lupa ou camera macro | inspecao de pontes e soldas frias |
| 1 | base de acrilico, FR-4 ou impressa em 3D | nunca usar chapa metalica exposta |
| varios | termo retratil, abracadeiras e etiquetas | identificar as duas pontas de cada fio |

Protoboard sem solda pode ser usada apenas para testar LED ou logica lenta.
Nao colocar nela o shunt, os sinais `OUTP/OUTN` ou o caminho de corrente final.

## 5. Expansao opcional, somente depois da corrente funcionar

| Qtd. | Item | Motivo | Onde comprar |
| ---: | --- | --- | --- |
| 1 | `AMC3330EVM` | medir tensao dinamica do rail e calcular `P(t) = V(t) * I(t)` | [TI](https://www.ti.com/tool/AMC3330EVM), DigiKey ou Mouser |
| 1 | `6N137` em `DIP-8` | marcador optico de inicio/fim; nao necessario para trigger por corrente | [Vishay](https://www.vishay.com/en/product/84732/), DigiKey ou Mouser |
| 1 | soquete `DIP-8` | montagem e troca do opto | loja local |
| varios | resistores/divisor PTH | definidos somente na revisao do canal de tensao ou marcador | nao comprar ainda |

Nao comprar `AMC3330DWE`, `AMC3302DWE`, `ADuM110N`, `ADuM120N`, `AO3400A` ou
passivos 0402/0603 avulsos para esta revisao. Eles pertenciam a alternativa de
PCBA personalizada e nao sao necessarios na bancada PTH.

## 6. Chicotes para as tres placas

Os chicotes nao devem ser montados antes de o medidor passar na carga
ficticia. Depois da aprovacao, fabricar um por placa:

| Placa | Ponto removivel | Acao mecanica permitida | Faixa inicial |
| --- | --- | --- | --- |
| `FRDM-MCXN947` | `J24` | remover o jumper e encaixar receptaculo femea isolado | HIGH |
| `NUCLEO-H723ZG` | `JP4` | remover o jumper e encaixar receptaculo femea isolado | HIGH |
| `nRF52840-DK` | alimentacao externa `P21` | usar plug compativel e as chaves documentadas, sem alterar pontes de solda | HIGH para verificar pico; LOW apenas se ficar abaixo de `40 mA` |

Requisitos de cada chicote:

- conector polarizado ou corpo marcado que impeca inversao;
- fios `RAIL_IN` e `RAIL_OUT` fisicamente distintos;
- contatos metalicos totalmente cobertos;
- etiqueta com placa, revisao e sentido `FONTE -> MCU`;
- teste de continuidade registrado pino a pino;
- sem garras jacare e sem jumper Dupont solto na medicao energizada.

O conector exato da Nordic deve ser confirmado na placa fisica antes da compra.

## 7. Ordem segura de aquisicao

1. Comprar NUCLEO, `AMC3302EVM`, proto-shield, placas universais e componentes
   da carga ficticia.
2. Montar primeiro o shield de ADC e a carga ficticia.
3. Montar as duas placas de shunt PTH.
4. Validar continuidade e isolamento sem energia.
5. Executar a validacao estatica e dinamica da secao 9 do documento 028.
6. Somente depois comprar/montar os tres chicotes.
7. Adiar `AMC3330EVM` e `6N137` ate que a medicao de corrente esteja estavel.

## 8. Custo que nao deve ser reduzido

Os dois itens que definem a confiabilidade do front-end sao o
`AMC3302EVM` original e os shunts Kelvin. Modulos genericos `ACS712`, `INA219`,
`INA226` e placas sem esquema conhecido nao sao equivalentes: eles podem ter
banda menor, conversao serial lenta, offset diferente ou nenhuma isolacao.

E aceitavel economizar em base mecanica, LEDs, bornes e placa universal. Nao e
aceitavel economizar removendo limite de corrente da fonte, isolamento do canal
analogico ou conexoes Kelvin.

## 9. Fontes de especificacao

- TI, [AMC3302EVM](https://www.ti.com/tool/AMC3302EVM) e
  [guia de usuario](https://www.ti.com/lit/ug/sbau330c/sbau330c.pdf);
- ST, [NUCLEO-G474RE](https://www.st.com/en/evaluation-tools/nucleo-g474re.html);
- Caddock, [Type SR Current Sense](https://www.caddock.com/online-catalog/mrktg-lit/TypeSR.pdf);
- Adafruit, [Proto-ScrewShield R3 PTH](https://www.adafruit.com/product/196);
- TI, [SN74HCT14N](https://www.ti.com/product/SN74HCT14/part-details/SN74HCT14N);
- onsemi, [FQP30N06L](https://www.onsemi.com/download/data-sheet/pdf/fqp30n06l-d.pdf).
