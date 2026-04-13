# Contexto Atual

## Objetivo geral

Este repositorio implementa um fluxo para:

1. receber um modelo `.tflite` quantizado
2. gerar partes do codigo C++ embarcado para TensorFlow Lite Micro
3. compilar firmware para a placa NXP `FRDM-MCXN947` / MCU `MCXN947`
4. gravar o firmware na placa
5. enviar entradas por serial
6. medir o tempo de inferencia
7. registrar resultados em CSV

O host de desenvolvimento e Linux. O firmware roda na MCU.

## Estado atual do ambiente

Ambiente do usuario validado nesta sessao:

- sistema: Ubuntu 24.04
- usuario: `christian`
- repositorio: `/home/christian/github/balas`
- Python virtualenv: `.venv`
- IDE: `MCUXpresso IDE`
- flash/debug: `LinkServer`
- serial da placa: `/dev/ttyACM0`
- placa detectada: `FRDM-MCXN947`

Ferramentas e caminhos relevantes confirmados:

- `MCUXpresso IDE`: `/usr/local/mcuxpressoide/ide/mcuxpressoide`
- `LinkServer`: `/usr/local/LinkServer/LinkServer`
- `stm32tflm`: encontrado na instalacao local do X-CUBE-AI em
  `/home/christian/opt/st/x-cube-ai/10.2.0/stedgeai-linux-10.2.0/Utilities/linux/stm32tflm`

## O que foi lido e usado como referencia

Documentos do repositorio lidos ou atualizados para montar o contexto:

- `docs/projeto-visao-geral.md`
- `docs/frdm-mcxn947-ubuntu-24.04-primeiro-teste.md`
- `docs/deploy-firmware-linkserver.md`
- `docs/deploy-terminal-output.txt`
- `docs/sanity-test-expectativas-tcc-vs-repositorio.md`
- `docs/configuracao-local-e-validacao.md`
- `docs/x-cube-ai-linux-v10.2.0-instalacao-e-teste.md`

Documento externo usado para reconstruir o caso de teste:

- `../mestrado/TG2_BrunoSilveira/TG2_Bruno_Silveira.pdf`

## O que foi entendido do projeto

- O repositorio automatiza o fluxo host + firmware para benchmarking de modelos TFLite quantizados em MCU.
- O firmware principal esta em `cpp-project/tflite-test/`.
- O fluxo principal de uso e o `automator.py`.
- O `automator.py` espera sempre:
  - um modelo `.tflite`
  - um diretorio de dataset com arquivos `.bin` em `float32`
  - um arquivo CSV de saida
- O dataset e enviado pela serial para a placa, e a placa retorna tempos de inferencia em microssegundos.

## Problemas que existiam no inicio da sessao

No inicio desta sessao, o projeto ainda tinha problemas de portabilidade e reproducao:

- caminhos hardcoded para ambiente local em partes do fluxo
- dependencia do `stm32tflm` sem descoberta automatica
- dependencia pratica de `/dev/ttyACM0` hardcoded
- falta de fixture versionado para sanity test
- ausencia de um `.tflite` diretamente utilizavel pelo `automator.py`
- ausencia de dataset `.bin` versionado para teste fim a fim
- documentacao insuficiente sobre como usar o `automator.py`
- rastreamento indevido de artefatos gerados do MCUXpresso

Esses pontos foram tratados ao longo da sessao.

## Ajustes de codigo e configuracao realizados

## 1. Configuracao local externalizada

Foi criado um mecanismo de configuracao local em:

- `python_scripts/config.py`
- `.balas.env.example`

Esse mecanismo permite configurar, sem editar codigo:

- `BALAS_SERIAL_PORT`
- `BALAS_STM32TFLM_BIN`
- `MCUXPRESSO_IDE_BIN`
- `MCUX_WORKSPACE_DIR`
- `MCUX_IMPORT_PROJECT`
- `BUILD_CONFIG`
- `LINKSERVER_ROOT`
- `PROBE_SERIAL`

## 2. Build e deploy tornados portaveis

Os scripts abaixo foram ajustados para usar configuracao local e defaults razoaveis:

- `compile.sh`
- `deploy.sh`

O objetivo foi remover dependencia de caminhos fixos da maquina original.

## 3. Descoberta automatica do `stm32tflm`

O estimador de tensor arena em `python_scripts/arena_estimator/estimator.py` agora procura o `stm32tflm` em:

- `BALAS_STM32TFLM_BIN`
- `PATH`
- locais comuns da instalacao do X-CUBE-AI no `$HOME`

## 4. Porta serial configuravel

O `automator.py` e o profiler passaram a aceitar `--serial-device`, com default vindo de:

- `BALAS_SERIAL_PORT`
- ou `/dev/ttyACM0`

## 5. Parametros operacionais adicionados ao `automator.py`

O `automator.py` hoje aceita:

- `--serial-device`
- `--arena-size`
- `--skip-compile`
- `--skip-deploy`

Isso viabiliza tanto:

- o fluxo completo com build e flash
- quanto o fluxo rapido reaproveitando o firmware ja gravado

## 6. Estabilidade do header do modelo gerado

O gerador em `python_scripts/code_generator/generator.py` foi ajustado para normalizar o simbolo de comprimento do modelo em `model_data.h` para:

```c
unsigned int model_data_len = ...;
```

Antes disso, o nome do simbolo dependia do caminho local do arquivo `.tflite` usado na execucao.

## 7. Scripts genericos adicionados

Foram adicionados dois scripts utilitarios reutilizaveis:

- `python_scripts/recover_tflite_from_header.py`
- `python_scripts/generate_float32_dataset.py`

Eles servem para:

- recuperar um `.tflite` a partir de `model_data.h`
- gerar datasets `.bin` em `float32` de forma deterministica

## Ambiente Python e dependencias

Foi criada a `.venv` do projeto e instaladas as dependencias Python necessarias.

Validacoes realizadas na `.venv`:

- `numpy`: OK
- `pyserial`: OK
- `tensorflow`: OK

Foi gerado:

- `docs/requirements.txt`

Esse arquivo registra o `pip freeze` do virtualenv para replicacao.

Observacao:

- `docs/requirements.txt` cobre dependencias Python
- nao cobre instalacao de `MCUXpresso`, `LinkServer` e `stm32tflm`

## X-CUBE-AI / ST Edge AI

Foi validado o conteudo do zip Linux baixado em `./assets`:

- o zip principal contem o `.pack` do CubeMX e o zip `stedgeai-linux`
- o zip `stedgeai-linux` contem `stm32tflm` e `stedgeai`

Foi criada documentacao especifica para isso:

- `docs/x-cube-ai-linux-v10.2.0-instalacao-e-teste.md`

Essa documentacao tambem corrige um erro operacional observado:

- o `.pack` e o `.zip` extraidos nao devem ser executados como comandos
- eles precisam ser extraidos e usados como artefatos, nao executados diretamente

## Estado atual da placa, serial e probe

Validacoes de hardware feitas nesta sessao:

- `/dev/ttyACM0` apareceu corretamente
- `LinkServer probes` encontrou a FRDM-MCXN947
- foi possivel enviar dados pela serial e receber tempos de inferencia da placa

Saida validada de probe:

```text
#  Description                                    Serial         Device    Board         Capabilities
---  ---------------------------------------------  -------------  --------  ------------  ----------------
1  MCU-LINK FRDM-MCXN947 (r0E7) CMSIS-DAP V3.128  EB04LLNGMJHMR  MCXN947   FRDM-MCXN947  DEBUG, VCOM, SIO
```

Conclusao atual:

- a placa esta conectada corretamente
- a serial esta funcional
- o `LinkServer` esta funcional no ambiente atual

## Descoberta importante sobre modelo e dataset

No inicio da sessao, nao existia no repositorio:

- um `.tflite` pronto para ser passado ao `automator.py`
- um dataset `.bin` versionado para sanity test

Foi encontrado apenas:

- `cpp-project/tflite-test/model/model_data.h`

Esse arquivo continha o modelo embutido em C.

Foi entao feita a recuperacao do `.tflite` a partir desse header e a validacao do modelo com TensorFlow Lite.

O que foi confirmado no modelo recuperado:

- tamanho: `94504` bytes
- entrada: `int8`
- shape de entrada: `1x32x32x3`
- saida: `int8`
- shape de saida: `1x10`
- `ops_count`: `21`

Esses dados batem com o caso de `Image Classification` descrito no PDF do TCC, associado ao uso de CIFAR-10.

## Fixture de sanity test criado e validado

Foi criado e versionado um fixture em:

- `testdata/sanity-model/`

Conteudo atual do fixture:

- `testdata/sanity-model/model_quant.tflite`
- `testdata/sanity-model/profiling_dataset/sample_001.bin` ate `sample_010.bin`
- `testdata/sanity-model/manifest.json`
- `testdata/sanity-model/README.md`

Esse fixture representa um caso pequeno e reproduzivel de sanity test.

Observacoes:

- o modelo veio da recuperacao de `model_data.h`
- o dataset versionado e sintetico e deterministico
- ele serve para sanity test de ambiente, serial, build e relatorio
- ele nao substitui um dataset real para avaliacao de acuracia

## Validacao ponta a ponta do `automator.py`

O `automator.py` foi validado com sucesso usando o fixture versionado e a placa conectada.

Comando validado:

```bash
source .venv/bin/activate
python automator.py \
  testdata/sanity-model/model_quant.tflite \
  testdata/sanity-model/profiling_dataset \
  /tmp/balas-sanity-results.csv \
  --arena-size 57344 \
  --serial-device /dev/ttyACM0 \
  --skip-compile \
  --skip-deploy
```

Resultado observado:

- `arena_size = 57344`
- `macs = 12501632`
- `avg_inference_us = 234708.2`
- `std_inference_us = 7.807688518377254`

Tambem foi validado um envio serial direto de um tensor aleatorio compativel com o modelo, com resposta da placa.

Conclusao:

- o fluxo minimo do `automator.py` esta funcional nesta maquina
- a placa responde pela serial
- o fixture atual e suficiente para sanity test reproduzivel

## Documentacao produzida ou atualizada hoje

Documentos existentes ou produzidos nesta sessao que agora fazem parte do contexto:

- `docs/configuracao-local-e-validacao.md`
- `docs/x-cube-ai-linux-v10.2.0-instalacao-e-teste.md`
- `docs/sanity-test-image-classification-recuperado.md`
- `docs/relatorio-ajustes-automator.md`
- `docs/tflite-recuperado-ajustes-e-uso.md`
- `docs/requirements.txt`

Esses arquivos cobrem:

- instalacao e validacao do ambiente
- X-CUBE-AI / ST Edge AI no Linux
- sanity test recuperado de `model_data.h`
- relatorio dos ajustes para o `automator.py`
- explicacao especifica sobre o `.tflite` recuperado
- snapshot das dependencias Python

## Higiene de repositorio realizada

Foram removidos do versionamento artefatos gerados do workspace do MCUXpresso e adicionadas regras de ignore para:

- `.venv`
- `__pycache__`
- `*.pyc`
- `cpp-project/.metadata/`
- `cpp-project/.mcuxpressoide_packages_support/`
- `cpp-project/tflite-test/.settings/`
- `cpp-project/tflite-test/Debug/`
- `cpp-project/tflite-test/Release/`

Isso evita poluir o repositorio com build local e metadados de IDE.

## Commits relevantes criados hoje

Commits produzidos nesta sessao:

- `b0f3b5d` `Make host tooling configurable and document setup`
- `fb2723b` `Stop tracking generated MCUXpresso artifacts`
- `92c0fa3` `Add sanity test fixture structure`
- `a21b97a` `Add reusable tooling for recovered TFLite sanity fixtures`
- `e556d05` `Add recovered image-classification sanity fixture`
- `4c9ec14` `Document automator setup and recovered TFLite usage`

## Estado atual do git

No fim desta etapa, o estado esperado do repositorio e:

- alteracoes relevantes desta sessao ja commitadas
- `assets/` ainda fora do versionamento

## Como retomar rapidamente em uma proxima sessao

Se a proxima sessao precisar apenas validar o ambiente e usar o `automator.py`, o caminho mais curto e:

1. confirmar que a placa aparece em `/dev/ttyACM0`
2. ativar a `.venv`
3. usar o fixture em `testdata/sanity-model`
4. rodar o comando validado do sanity test

Comandos uteis:

```bash
ls -l /dev/ttyACM*
/usr/local/LinkServer/LinkServer probes
source .venv/bin/activate
python automator.py \
  testdata/sanity-model/model_quant.tflite \
  testdata/sanity-model/profiling_dataset \
  /tmp/balas-sanity-results.csv \
  --arena-size 57344 \
  --serial-device /dev/ttyACM0 \
  --skip-compile \
  --skip-deploy
```

## Resumo curto para retomada

O contexto essencial para a proxima sessao e:

- o fluxo host + serial + CSV esta funcional
- o `automator.py` foi tornado configuravel e documentado
- o `stm32tflm` local foi encontrado e validado
- existe um `.tflite` recuperado e versionado para sanity test
- existe um dataset `.bin` versionado e deterministico
- a FRDM-MCXN947 foi detectada e respondeu ao profiling
- os commits principais desta sessao ja foram criados
- `assets/` continua fora do versionamento
