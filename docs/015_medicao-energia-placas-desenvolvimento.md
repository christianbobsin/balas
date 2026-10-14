# Medicao de energia nas tres placas de desenvolvimento

Documento criado em 2026-04-27 e revisado em 2026-08-28 para registrar os
pontos de medicao do rail do microcontrolador nas tres placas usadas pelo
BALAS. O projeto completo do medidor autonomo, da carga de validacao e do
procedimento de captura esta em
[025_projeto-medidor-corrente-dc-instantanea.md](025_projeto-medidor-corrente-dc-instantanea.md).

Restricao desta revisao: nenhuma placa BALAS pode ser soldada, dessoldada,
cortada ou ter ponte de solda alterada. Somente jumpers removiveis, chaves e
conectores ja existentes podem ser usados.

## Resumo

| Placa | Ponto em serie | Rail observado | Preparacao |
| --- | --- | --- | --- |
| NXP FRDM-MCXN947 | `J24 / IDD_MCU` | `P3V3_MCU` | Remover o shunt de `J24` e inserir o instrumento entre `IDD_IN` e `IDD_OUT`. |
| ST NUCLEO-H723ZG | `JP4 / IDD` | `VDD_MCU` | Remover o jumper de `JP4` e inserir o instrumento entre `VDD` e `VDD_MCU`. |
| Nordic nRF52840-DK | entrada de alimentacao externa `P21` | corrente entregue pela fonte externa ao dominio `VDD` | Alimentar `P21` atraves do medidor, com `SW9 = VDD`, `SW10 = ON` (`VEXT -> nRF`) e `SW6 = nRF ONLY`; nao abrir `SB40` nem `SB41`. |

Esses pontos nao sao medidores completos. Em NXP e ST, eles interrompem o rail
para que um shunt ou amperimetro seja colocado em serie. Na Nordic, o medidor
fica em serie com a fonte externa ligada a `P21`. A partir das amostras de
corrente:

```text
P(t) = Vrail(t) * I(t)
E = integral(P(t) dt)
```

Para detectar aumentos curtos de consumo, um multimetro ou monitor I2C de baixa
taxa nao e suficiente. O documento `025` define um front-end isolado ligado a
uma placa de aquisicao dedicada, sem depender de osciloscopio.

## O que a medicao representa

A medicao nos pontos selecionados e muito melhor que medir a corrente total no
USB, mas ainda representa a corrente que atravessa o caminho de alimentacao
escolhido. Ela nao e uma sonda interna do nucleo da CPU. Capacitores de
desacoplamento, reguladores, dominios auxiliares e componentes que compartilham
o rail podem alterar o formato observado.

Consequencias praticas:

- pulsos internos muito rapidos podem ser fornecidos primeiro pelos capacitores
  locais e aparecer no shunt como uma reposicao de carga mais lenta;
- a corrente de interfaces e perifericos no mesmo rail deve ser mantida igual
  ou documentada;
- a comparacao deve usar o mesmo ponto logico da inferencia, a mesma janela e o
  mesmo criterio de baseline;
- corrente instantanea, potencia e energia sao metricas diferentes e devem ser
  registradas separadamente.

Para nao apresentar precisao falsa, os resultados devem identificar a classe
da conexao:

- `A - rail dedicado`: NXP em `J24` e ST em `JP4`; preparacao inteiramente
  reversivel, removendo apenas um shunt/jumper;
- `B - alimentacao externa do SoC`: Nordic em `P21`, usando somente as chaves
  da placa. E a melhor rota sem adulteracao, mas pode incluir fuga residual ou
  alguma carga que permaneca ligada ao dominio `VDD`;
- a rota Nordic `P22/SB40`, mais direta para `VDD_nRF`, nao sera usada porque
  exige cortar `SB40` na configuracao original e depois soldar para restaura-la.

Comparacoes de aumento sobre o baseline continuam validas na classe `B`, desde
que configuracao, tensao e perifericos sejam mantidos iguais. Valores absolutos
Nordic devem ser publicados separadamente dos resultados de classe `A`.

## Valores de referencia, nao resultados medidos

Os numeros abaixo servem apenas para selecionar a faixa inicial do medidor.
Eles nao substituem a medicao do firmware BALAS real.

| Placa | MCU | Tensao do MCU | Referencia de consumo ativo | Baixo consumo de referencia |
| --- | --- | --- | --- | --- |
| FRDM-MCXN947 | NXP MCXN947 | `1,71 V` a `3,6 V` | Ate `57 uA/MHz` na condicao de menor consumo ativo publicada. | `6 uA` em Power-down com RTC e `512 KB` de SRAM retida; `2 uA` em Deep Power-down com RTC e `32 KB` retidos. |
| NUCLEO-H723ZG | ST STM32H723ZG | `1,62 V` a `3,6 V` em `VDD`/`VDDLDO`/`VDDA` | `145 mA` tipicos em Run a `550 MHz` na condicao especificada pelo datasheet. | Stop a partir de `0,52 mA`; Standby na ordem de poucos microamperes, conforme a configuracao de RTC e SRAM. |
| nRF52840-DK | Nordic nRF52840 | `1,7 V` a `3,6 V` em `VDD`; `2,5 V` a `5,5 V` em `VDDH` | `52 uA/MHz` rodando CoreMark a partir da Flash, ou aproximadamente `3,3 mA` a `64 MHz` na condicao publicada. | `0,4 uA` em System OFF sem retencao de RAM e `1,5 uA` em System ON sem retencao com wake por RTC, a `3 V`. |

## Esquematicos locais

| Placa | Arquivo | Evidencia principal |
| --- | --- | --- |
| FRDM-MCXN947 | [nxp-frdm-mcxn947-90818-mcxn947sh-schematic.pdf](hardware-pdfs/nxp-frdm-mcxn947-90818-mcxn947sh-schematic.pdf) | Folha `USB & PWR`: `J24` entre `P3V3` e `P3V3_MCU`. |
| NUCLEO-H723ZG | [st-nucleo-h723zg-mb1364-h723zg-e01-schematic.pdf](hardware-pdfs/st-nucleo-h723zg-mb1364-h723zg-e01-schematic.pdf) | Folha `MCU 144 POWER`: `JP4 / IDD Measurement` entre `VDD` e `VDD_MCU`. |
| nRF52840-DK | [nordic-nrf52840-dk-pca10056-schematic-and-pcb.pdf](hardware-pdfs/nordic-nrf52840-dk-pca10056-schematic-and-pcb.pdf) | Folha `Power supply`: entrada externa `P21`, seletores `SW9`/`SW10` e chave `SW6`; `P22/SB40` permanece documentado apenas como rota excluida. |

## NXP FRDM-MCXN947

O ponto `J24 / IDD_MCU` fica entre a saida geral `P3V3` e o rail
`P3V3_MCU`. A documentacao do exemplo `power_manager_test` da NXP confirma o
seguinte mapeamento:

| Sinal | Ponto | Funcao |
| --- | --- | --- |
| `IDD_IN` | `J24-1` | Lado da fonte, vindo de `P3V3`. |
| `IDD_OUT` | `J24-2` | Lado da carga, seguindo para `P3V3_MCU`. |
| `VSS` | `J10-4` | Referencia usada pelo MCU-Link Debug Probe. |

Procedimento resumido:

1. Desligar e desconectar todas as fontes da placa.
2. Remover o shunt de `J24`.
3. Ligar `IN` do medidor a `J24-1` e `OUT` a `J24-2`.
4. Confirmar continuidade e polaridade antes de energizar.
5. Medir tambem a tensao no lado `P3V3_MCU` para calcular potencia.

Nao medir em `P5V0`, no USB ou no `P3V3` geral se o objetivo for isolar o rail
do MCU. Se a placa tiver sido modificada para separar `VDD_ANA`, `VDD_BAT`,
`VDD_USB` ou `VDD_CORE_SYS`, reconfirmar no esquematico quais dominios ainda
atravessam `J24`.

## ST NUCLEO-H723ZG

O esquematico da variante `MB1364-H723ZG-E01` identifica `JP4` como
`IDD Measurement`. O lado de entrada e `VDD`; o lado de saida e `VDD_MCU`.

Procedimento resumido:

1. Desligar e desconectar todas as fontes da placa.
2. Remover o jumper de `JP4`.
3. Ligar `IN` do medidor ao pino `VDD` e `OUT` ao pino `VDD_MCU`.
4. Confirmar continuidade e polaridade antes de energizar.
5. Medir a tensao em `VDD_MCU` durante a captura.

Na revisao `E01`, o manual `UM2407` informa que a medicao de `IDD` pode ser
realizada em Standby; o Ethernet PHY foi separado de `VDD_MCU`. Essa conclusao
nao deve ser transferida para revisoes antigas sem verificar a identificacao da
placa.

## Nordic nRF52840-DK

O guia da Nordic oferece alimentacao direta e reversivel pelo conector `P21`.
Essa sera a unica rota permitida neste projeto. Nao usar `P22`, `P23`, `SB40`
ou `SB41`.

Procedimento sem solda e sem corte:

1. Programar o firmware autonomo antes da medicao.
2. Desligar e desconectar todas as fontes.
3. Colocar `SW9` na posicao `VDD`.
4. Colocar `SW6` em `nRF ONLY`, isolando o interface MCU, LEDs e sinais da
   aplicacao conforme o guia da placa.
5. Colocar `SW10` em `ON`, habilitando `VEXT -> nRF`.
6. Ajustar uma fonte regulada entre `1,7 V` e `3,6 V`; usar inicialmente
   `3,0 V` e limite de corrente baixo.
7. Com tudo desligado, ligar o positivo da fonte a `RAIL_IN` do medidor,
   `RAIL_OUT` ao positivo de `P21` e o retorno ao `GND` de `P21`. Usar a
   polaridade impressa na placa e confirma-la com o esquematico e o multimetro;
   nao confiar apenas na orientacao fisica do conector.
8. Alimentar separadamente o restante do DK em `5 V` para o seguidor de tensao,
   como exige o guia da Nordic. Essa fonte tambem deve flutuar em relacao ao
   computador e nao deve abrir terminal na VCOM. Sua corrente de `5 V` nao
   atravessa o shunt de `P21`, mas a condicao deve ser registrada.
9. Executar `ZERO`, energizar a fonte de `P21` e confirmar a tensao antes de
   iniciar a captura.

O resultado e a corrente entregue pelo caminho externo `P21` ao dominio `VDD`,
nao uma garantia de corrente matematicamente exclusiva do nucleo. O modo
`nRF ONLY` reduz a interferencia, mas a configuracao da memoria externa e fugas
residuais ainda podem contribuir. Para detectar o aumento provocado por
processamento, medir um baseline imediatamente anterior e usar `delta_I` e
energia incremental.

Como o protocolo BALAS atual usa a VCOM para enviar o tensor, a medicao de menor
interferencia requer um firmware de ensaio autonomo: tensor pregravado, disparo
local e marcador GPIO de inicio/fim da inferencia. A serial pode continuar sendo
usada em ensaios exploratorios, mas essa condicao deve ser registrada e nao deve
ser misturada com a captura autonoma.

## Criterio comum para as tres placas

- mesmo modelo e mesma entrada;
- mesma definicao de inicio e fim de inferencia;
- mesma faixa do medidor quando ela nao comprometer resolucao;
- mesma taxa de amostragem e largura de banda;
- mesma politica para clocks, caches, LEDs, debug e perifericos;
- nenhuma conexao de dados com o computador durante a captura e fontes do DUT
  flutuantes em relacao ao terra do computador;
- baseline imediatamente antes de cada inferencia;
- tensao real do rail, nao apenas `3,3 V` presumidos;
- pelo menos corrente media, pico, aumento sobre o baseline, duracao e energia.

## Fontes oficiais

- NXP, `power_manager_test` para FRDM-MCXN947:
  https://mcuxpresso.nxp.com/mcuxsdk/latest/html/examples/_boards/frdmmcxn947/demo_apps/power_manager_test/bm/example_board_readme.html
- ST, manual `UM2407` das Nucleo-144 `MB1364`:
  https://www.st.com/resource/en/user_manual/um2407-stm32h7-nucleo144-board-stmicroelectronics.pdf
- Nordic, medicao de corrente na nRF52840-DK:
  https://docs.nordicsemi.com/r/bundle/ug_nrf52840_dk/page/ug/dk/hw_measure_current.html
- Nordic, alimentacao direta pelo conector `P21`:
  https://docs.nordicsemi.com/r/bundle/ug_nrf52840_dk/page/ug/dk/direct_supply.html
- Nordic, modo `nRF ONLY`:
  https://docs.nordicsemi.com/r/bundle/ug_nrf52840_dk/page/ug/dk/nrf_only_mode.html
- Nordic, selecao da fonte de alimentacao:
  https://docs.nordicsemi.com/r/bundle/ug_nrf52840_dk/page/ug/dk/power_source.html
- Nordic, preparo de `P22/SB40` (rota consultada e deliberadamente excluida):
  https://docs.nordicsemi.com/r/bundle/ug_nrf52840_dk/page/ug/dk/prepare_board.html
- Nordic, Product Specification do nRF52840:
  https://docs.nordicsemi.com/r/bundle/ps_nrf52840/
