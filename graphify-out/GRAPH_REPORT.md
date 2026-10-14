# Graph Report - docs  (2026-09-03)

## Corpus Check
- 4 files · ~44,937 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 240 nodes · 134 edges · 125 communities (12 shown, 113 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 14 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Targets NXP e STM32
- Medidor Isolado e Aquisicao
- Montagem PTH e Validacao
- Configuracao e Fase 1
- Pipeline Host e MCU
- Experimentos e TCC
- Bring-up FRDM e LinkServer
- Modelo e Dataset Sanity
- Medicao Nordic sem Solda
- Arduino Avancado versus NUCLEO
- Patches STM32 CMSIS-NN
- Rails Dedicados NXP ST
- Adaptadores sem Adulteracao
- Comparacao STM32 TFLM versus NXP
- Espera pos-deploy STM32
- Fallback Conv2D 3x3 de referencia
- Posicionamento em ITCM DTCM e
- Otimizacao TFLM CMSIS-NN com -O3
- Falha do overlay scratch nativo
- Relatorio de desempenho STM32 vs
- BALAS sanity benchmark
- Scratch buffer CMSIS-NN para Conv2D
- Scratch persistente na arena TFLM
- Recriacao do interpretador por inferencia
- Arena STM32 TFLM de 81920
- Correcao de scratch Conv2D
- Pendencia do overlay scratch TFLM
- Resultado STM32 TFLM 42720.8 us
- Status STM32 TFLM apos correcao
- artifacts/stm32 tflm suite.csv
- automator.py Concept
- Suite de benchmark reproduzivel
- Contagem de MACs do modelo
- CSV de resultados BALAS
- FRDM-MCXN947 Concept
- LinkServer Concept
- MCUXpresso IDE
- Pipeline host mais MCU do
- Protocolo serial BALAS de quatro
- Roteiro de reproducao BALAS na
- Tensor arena da FRDM-MCXN947
- TensorFlow Lite Micro
- Criterios de validacao da reproducao
- AP-Protect do nRF52840
- Firmware Nordic bring-up
- nrfutil device recover
- Projetos embarcados isolados por alvo
- Firmware Nordic TFLM
- Nordic nRF52840 Cortex-M4F
- Nordic nRF52840-DK PCA10056
- nRF Connect SDK v3.4.0
- nRF Util
- Port Nordic nRF52840-DK do BALAS
- Protocolo binario Nordic do benchmark
- Resultado nRF52840 704854.8 us
- DTR e controle de fluxo
- Sanity benchmark Nordic
- TFLM com kernels CMSIS-NN no
- VCOM0 ligada a UART0
- Zephyr 4.4
- Arm Cortex-M33
- LinkServer RedlinkMulti Driver
- Log de deploy da FRDM-MCXN947
- MCU-LINK FRDM-MCXN947 probe
- MCXN947 Concept
- Amostras seriais de latencia em
- Serial Wire Debug
- tflite-test.axf Concept
- PCA10056 connectors and GPIO
- PCA10056 schematic and PCB
- PCA10056 Interface MCU
- PCA10056 NFC QSPI and I2C
- nRF52840 Development Board PCA10056
- nRF52840 MCU
- PCA10056 power supply
- PCA10056 SWD debug paths
- PCA10056 VCOM and nRF52 UART
- PCA10095 connectors and GPIO
- PCA10095 schematic and PCB
- PCA10095 Interface MCU
- PCA10095 NFC QSPI and USB
- nRF5340 Development Board PCA10095
- nRF5340 radio SoC
- PCA10095 power supply
- PCA10095 SWD debug paths
- PCA10095 VCOM and UART
- FRDM CAN and Ethernet PHY
- FRDM-MCXN947 schematic
- FRDM-MCXN947 Concept
- FRDM headers switches and LEDs
- FRDM MCU-Link interface
- MCXN947 SoC
- FRDM SD QSPI and sensor
- FRDM SWD and UART debug
- FRDM USB and power subsystem
- NUCLEO connectors and Arduino headers
- NUCLEO-H723ZG MB1364 schematic
- NUCLEO Ethernet PHY and RJ45
- NUCLEO-H723ZG Concept
- NUCLEO main power board
- ST-LINK V3E
- STM32H723ZGT6 MCU
- NUCLEO SWD debug path
- NUCLEO USB full-speed subsystem
- ST-LINK virtual COM port
- Keras 3.14.0
- NumPy 2.4.4
- PySerial 3.5
- Dependencias Python do BALAS
- TensorFlow 2.21.0
- Ativacoes e buffers scratch
- A arena no TensorFlow Lite
- Pesos do modelo na Flash
- Pre-alocacao estatica de RAM
- Reutilizacao de memoria entre tensores
- Tensor arena TFLM
- Trade-off de dimensionamento da arena
- MACs como proxy de latencia
- MLPerf Tiny
- Neural Architecture Search para TinyML
- Quantizacao int8 para TinyML
- Redes neurais artificiais e profundas
- Resumo do Capitulo 2
- STM32Cube.AI Concept
- TensorFlow Lite for Microcontrollers

## God Nodes (most connected - your core abstractions)
1. `Comparativo sanity FRDM vs NUCLEO` - 7 edges
2. `NUCLEO-G474RE como baseline de menor risco` - 7 edges
3. `Contexto Atual` - 5 edges
4. `Pipeline Python principal` - 5 edges
5. `TCC de Bruno Silveira` - 5 edges
6. `Sanity Test Recuperado de model_data.h` - 5 edges
7. `Alvo STM32H723ZG` - 5 edges
8. `Retomada TFLM STM32` - 5 edges
9. `Medidor autonomo de corrente DC instantanea` - 5 edges
10. `Lista de compras do medidor modular PTH` - 5 edges

## Surprising Connections (you probably didn't know these)
- `Ordem de resolucao de configuracao` --semantically_similar_to--> `Configuracao local externalizada`  [INFERRED] [semantically similar]
  004_configuracao-local-e-validacao.md → 001_context.md
- `Pipeline Python principal` --semantically_similar_to--> `Pipeline principal do automator`  [INFERRED] [semantically similar]
  003_mapa-python-scripts.md → 002_projeto-visao-geral.md
- `Firmware como servidor UART` --semantically_similar_to--> `Protocolo serial binario de profiling`  [INFERRED] [semantically similar]
  009_sanity-test-expectativas-tcc-vs-repositorio.md → 002_projeto-visao-geral.md
- `Orquestracao do automator` --semantically_similar_to--> `Pipeline Python principal`  [INFERRED] [semantically similar]
  012_relatorio-ajustes-automator.md → 003_mapa-python-scripts.md
- `AMC3302EVM pronto com bornes e barreira galvanica` --semantically_similar_to--> `AMC3302EVM canal isolado de corrente`  [INFERRED] [semantically similar]
  028_diagrama-montagem-medidor-corrente-pth.md → 025_projeto-medidor-corrente-dc-instantanea.md

## Hyperedges (group relationships)
- **Arquitetura do medidor isolado com EVM** — 025_projeto_medidor_corrente_dc_instantanea_amc3302evm, 025_projeto_medidor_corrente_dc_instantanea_nucleo_g474re, 025_projeto_medidor_corrente_dc_instantanea_faixas_high_low [EXTRACTED 1.00]
- **Comparacao das placas de aquisicao** — 027_por_que_nucleo_g474re_em_vez_de_arduino_escolha_nucleo_g474re, 027_por_que_nucleo_g474re_em_vez_de_arduino_arduino_giga_r1_wifi, 027_por_que_nucleo_g474re_em_vez_de_arduino_arduino_portenta_h7 [EXTRACTED 1.00]
- **Montagem PTH por blocos prontos** — 028_diagrama_montagem_medidor_corrente_pth_amc3302evm, 028_diagrama_montagem_medidor_corrente_pth_shield_padrao_mecanico_uno_v3, 028_diagrama_montagem_medidor_corrente_pth_shunts_caddock_sr10, 028_diagrama_montagem_medidor_corrente_pth_carga_sn74hct14n_fqp30n06l [EXTRACTED 1.00]
- **Rotas de medicao sem adulterar as tres placas** — docs_015_medicao_energia_placas_desenvolvimento_frdm_j24, docs_015_medicao_energia_placas_desenvolvimento_nucleo_jp4, docs_015_medicao_energia_placas_desenvolvimento_nordic_p21 [EXTRACTED 1.00]
- **Fluxo BALAS host MCU e relatorio** — docs_002_projeto_visao_geral_pipeline_automator, docs_009_sanity_test_expectativas_tcc_vs_repositorio_firmware_servidor_uart, docs_009_sanity_test_expectativas_tcc_vs_repositorio_csv_gerado_no_host, docs_002_projeto_visao_geral_protocolo_serial_binario [EXTRACTED 1.00]
- **Port STM32 com backends ST Edge AI e TFLM** — docs_016_port_stm32_alvo_stm32h723zg, docs_016_port_stm32_backend_st_edge_ai, docs_016_port_stm32_backend_tflm_stm32, docs_018_tflm_stm32_build_biblioteca_tflm_cortex_m7 [EXTRACTED 1.00]
- **Recuperacao e otimizacao TFLM STM32 CMSIS-NN** — docs_019_tflm_stm32_retomada_diagnostico_marcadores_uart_rqgdvw, docs_020_tflm_stm32_cmsis_nn_reentrada_e_fallbacks_reconstrucao_interpretador_por_inferencia, docs_020_tflm_stm32_cmsis_nn_reentrada_e_fallbacks_scratch_persistente_na_arena, docs_020_tflm_stm32_cmsis_nn_reentrada_e_fallbacks_resultado_tflm_otimizado [INFERRED 0.95]

## Communities (125 total, 113 thin omitted)

### Community 0 - "Targets NXP e STM32"
Cohesion: 0.10
Nodes (23): Abstracoes STM32 de serial timer build e deploy, Alvo NXP MCXN947, Alvo STM32H723ZG, Backend STM32 ST Edge AI, Backend STM32 TFLM, Novo alvo STM32 paralelo ao NXP, Port para STM32 NUCLEO-H723ZG, Baseline FRDM TFLM 234708 us (+15 more)

### Community 1 - "Medidor Isolado e Aquisicao"
Cohesion: 0.14
Nodes (17): AMC3330EVM opcional para tensao dinamica, Arquitetura isolada baseada no AMC3302EVM pronto, Medidor autonomo de corrente DC instantanea, Modo BURST de 4 MS/s e 2,048 ms, Modo PROFILE para potencia e energia, NUCLEO-G474RE dedicada a aquisicao, AMC3330EVM e 6N137 adiados para segunda etapa, Lista de compras do medidor modular PTH (+9 more)

### Community 2 - "Montagem PTH e Validacao"
Cohesion: 0.16
Nodes (14): AMC3302EVM canal isolado de corrente, Carga ficticia PTH com RSTEP1 de 120 ohm, Faixas HIGH e LOW com shunts Kelvin PTH, Blocos prontos PTH em vez de PCBA SMD personalizada, Carga ficticia PTH com RSTEP1 de 120 ohm, DigiKey Mouser TI ST Adafruit e fornecedores locais, Kit obrigatorio da primeira etapa, Shunts Kelvin Caddock SR10 HIGH e LOW (+6 more)

### Community 3 - "Configuracao e Fase 1"
Cohesion: 0.17
Nodes (13): Configuracao local externalizada, Contexto Atual, Fase 1 Image Classification, Fixture versionado sanity-model, Pipeline BALAS host-firmware, Build headless portavel, Configuracao Local e Validacao, Ordem de resolucao de configuracao (+5 more)

### Community 4 - "Pipeline Host e MCU"
Cohesion: 0.15
Nodes (13): Arquitetura host e MCU, Bug de tamanho em input e output, Pipeline principal do automator, Protocolo serial binario de profiling, Visao Geral do Projeto, Mapa de python_scripts, Pipeline experimental de benchmark, Pipeline Python principal (+5 more)

### Community 5 - "Experimentos e TCC"
Cohesion: 0.18
Nodes (11): CSV gerado no host, CSV simplificado do repositorio, Expectativas do TCC vs Repositorio, TCC de Bruno Silveira, Fase 1 Image Classification, Grade de 96 variantes de image classification, Baseline MLCommons Tiny com CIFAR-10, Resultado do lote de 8 variantes (+3 more)

### Community 6 - "Bring-up FRDM e LinkServer"
Cohesion: 0.20
Nodes (10): Compatibilidade legado no Ubuntu 24.04, FRDM-MCXN947, MCU-Link debug probe e VCP, Primeiro Teste FRDM-MCXN947 no Ubuntu 24.04, Deploy de Firmware com LinkServer, Fluxo de deploy NXP, Selecao explicita do probe por serial, Niveis de validacao dos scripts (+2 more)

### Community 7 - "Modelo e Dataset Sanity"
Cohesion: 0.29
Nodes (7): Coerencia entre modelo host e firmware, Dataset float32 deterministico, Recuperacao do modelo a partir de model_data.h, TFLite Recuperado, Limite do dataset sintetico, Perfil do modelo sanity 1x32x32x3 int8, Sanity Test Recuperado de model_data.h

### Community 8 - "Medicao Nordic sem Solda"
Cohesion: 0.33
Nodes (6): Delta de corrente sobre baseline, Firmware autonomo de medicao, Medicao classe B - alimentacao externa do SoC, nRF52840-DK alimentacao direta P21, nRF only mode, Restricao sem solda nas placas BALAS

### Community 9 - "Arduino Avancado versus NUCLEO"
Cohesion: 0.60
Nodes (5): Arduino GIGA R1 WiFi como candidata avancada, Arduino Portenta H7 como candidata avancada, Modelo Arduino anterior nao identificado e comparacao com Uno removida, Reavaliacao Arduino mediante pinagem DMA taxa ruido e skew comprovados, STM32H747 com ADC de ate 16 bits e 3,6 MS/s

### Community 10 - "Patches STM32 CMSIS-NN"
Cohesion: 0.50
Nodes (4): Clock cache com USE_PWR_LDO_SUPPLY, Marcadores UART RQGDVW, Patches CMSIS-NN com fallback seletivo, TFLM STM32 com kernels de referencia funcional

### Community 11 - "Rails Dedicados NXP ST"
Cohesion: 0.67
Nodes (3): FRDM-MCXN947 J24 IDD_MCU, Medicao classe A - rail dedicado, NUCLEO-H723ZG JP4 IDD

## Knowledge Gaps
- **137 isolated node(s):** `Fixture versionado sanity-model`, `Fase 1 Image Classification`, `Visao Geral do Projeto`, `Bug de tamanho em input e output`, `Mapa de python_scripts` (+132 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **113 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TCC de Bruno Silveira` connect `Experimentos e TCC` to `Pipeline Host e MCU`, `Modelo e Dataset Sanity`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `Sanity Test Recuperado de model_data.h` connect `Modelo e Dataset Sanity` to `Targets NXP e STM32`, `Experimentos e TCC`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `Contexto Atual` connect `Configuracao e Fase 1` to `Experimentos e TCC`, `Bring-up FRDM e LinkServer`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Pipeline Python principal` (e.g. with `Pipeline principal do automator` and `Orquestracao do automator`) actually correct?**
  _`Pipeline Python principal` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Fixture versionado sanity-model`, `Fase 1 Image Classification`, `Visao Geral do Projeto` to the rest of the system?**
  _137 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Targets NXP e STM32` be split into smaller, more focused modules?**
  _Cohesion score 0.10276679841897234 - nodes in this community are weakly interconnected._
- **Should `Medidor Isolado e Aquisicao` be split into smaller, more focused modules?**
  _Cohesion score 0.13970588235294118 - nodes in this community are weakly interconnected._