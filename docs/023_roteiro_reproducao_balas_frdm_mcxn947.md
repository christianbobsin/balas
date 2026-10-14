# Roteiro de reproducao do projeto de Bruno usando FRDM-MCXN947

## Ideia central

O projeto de Bruno mede, em uma placa real, quanto tempo uma rede neural
quantizada leva para executar inferencia. A reproducao neste repositorio usa a
`FRDM-MCXN947` como alvo embarcado e um computador Linux como maquina de apoio.

A divisao do sistema e:

- no computador: preparar modelo, gerar codigo, compilar firmware, gravar a
  placa, enviar amostras pela serial e salvar CSV
- na FRDM-MCXN947: receber uma entrada, executar TensorFlow Lite Micro e
  devolver o tempo de inferencia em microssegundos

O resultado final esperado e um arquivo CSV com latencia real medida na MCU,
MACs do modelo e informacoes de memoria. Esse CSV e a base para comparar a
latencia real com estimativas, que e a ideia principal do experimento.

## Visao do fluxo completo

O fluxo inteiro acontece nesta ordem:

1. instalar as ferramentas no computador
2. conectar e validar a FRDM-MCXN947
3. configurar o repositorio localmente
4. escolher um modelo `.tflite` quantizado e um dataset de entradas `.bin`
5. estimar ou definir manualmente a tensor arena
6. calcular os MACs do modelo
7. gerar os arquivos C++ do firmware
8. compilar o projeto no MCUXpresso em modo headless
9. gravar o firmware na placa com LinkServer
10. enviar entradas pela serial
11. medir o tempo de inferencia na placa
12. salvar os resultados em CSV
13. analisar as correlacoes e comparar com o trabalho original

## 1. Preparar o computador

O host recomendado e Ubuntu/Linux. Instale os pacotes basicos:

```bash
sudo apt update
sudo apt install -y \
  git curl wget unzip xz-utils tar \
  build-essential cmake ninja-build \
  libusb-1.0-0 udev \
  python3 python3-venv python3-pip \
  xxd picocom minicom
```

Adicione o usuario ao grupo da serial:

```bash
sudo usermod -aG dialout "$USER"
```

Depois disso, faca logout/login para a permissao valer.

Tambem sao necessarios:

- `MCUXpresso IDE`, usado para compilar o projeto da NXP
- `LinkServer`, usado para gravar o firmware na placa
- Python com `tensorflow`, `numpy` e `pyserial`
- opcionalmente `stm32tflm`/X-CUBE-AI para estimar arena automaticamente

## 2. Validar a FRDM-MCXN947

Conecte a placa pela porta USB do `MCU-Link`. No Linux, verifique se a serial
apareceu:

```bash
ls /dev/ttyACM*
```

O resultado esperado e algo como:

```text
/dev/ttyACM0
```

Teste se a porta abre:

```bash
picocom -b 115200 /dev/ttyACM0
```

Para sair:

```text
Ctrl+A
Ctrl+X
```

Se aparecer `Permission denied`, o problema e permissao de serial. Se nao
aparecer `/dev/ttyACM0`, a placa pode ter enumerado em outro indice, como
`/dev/ttyACM1`.

## 3. Configurar o repositorio

Na raiz do repositorio:

```bash
cp .balas.env.example .balas.env
```

Edite `.balas.env` apenas se algum caminho for diferente no computador. Para a
FRDM-MCXN947, o alvo padrao e `nxp`.

Campos importantes:

- `BALAS_SERIAL_PORT=/dev/ttyACM0`
- `BALAS_TARGET=nxp`
- `MCUXPRESSO_IDE_BIN=/usr/local/mcuxpressoide/ide/mcuxpressoide`
- `MCUX_WORKSPACE_DIR=<repo>/cpp-project`
- `LINKSERVER_ROOT=/usr/local/LinkServer`
- `PROBE_SERIAL=<serial do probe, se houver mais de uma placa>`

Se houver apenas uma placa conectada, normalmente `PROBE_SERIAL` pode ficar
vazio e o LinkServer tenta selecionar automaticamente.

## 4. Entender os arquivos principais

O projeto embarcado da FRDM fica em:

```text
cpp-project/tflite-test/
```

Os arquivos mais importantes sao:

- `cpp-project/tflite-test/source/MCXN947_Project.cpp`
  - inicializa a placa
  - cria o objeto `MyModel`
  - entra em loop lendo entrada pela serial
  - mede o tempo de inferencia
  - devolve 4 bytes com o tempo em microssegundos

- `cpp-project/tflite-test/model/model.cpp`
  - carrega o modelo `.tflite` convertido para C
  - configura o `MicroMutableOpResolver`
  - aloca a `tensor_arena`
  - quantiza entrada `float32 -> int8`
  - executa `interpreter.Invoke()`
  - dequantiza a saida

- `automator.py`
  - orquestra o fluxo completo no computador
  - estima arena, calcula MACs, gera codigo, compila, grava, mede e salva CSV

- `compile.sh`
  - compila o projeto NXP usando MCUXpresso headless

- `deploy.sh`
  - grava o `.axf` na placa usando LinkServer

## 5. Preparar modelo e dataset

O modelo precisa estar em formato `.tflite` quantizado. O dataset de profiling
deve ser uma pasta com arquivos `.bin`, cada um contendo uma entrada em
`float32`.

O exemplo reduzido ja versionado usa:

```text
testdata/sanity-model/model_quant.tflite
testdata/sanity-model/profiling_dataset/
```

Esse exemplo serve para validar que o pipeline funciona antes de tentar varios
modelos.

## 6. Rodar o fluxo completo com `automator.py`

Crie e ative o ambiente Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r docs/requirements.txt
```

Para rodar o fluxo completo:

```bash
python3 automator.py \
  testdata/sanity-model/model_quant.tflite \
  testdata/sanity-model/profiling_dataset \
  results.csv \
  --serial-device /dev/ttyACM0 \
  --arena-size 57344
```

O que acontece internamente:

1. usa a arena informada em `--arena-size`
2. calcula os MACs do modelo
3. gera `model.cpp`, `model.h` e `model_data.h`
4. chama `./compile.sh`
5. chama `./deploy.sh`
6. envia cada `.bin` pela serial
7. recebe da FRDM um `int32` little-endian com o tempo de inferencia
8. grava media e desvio no CSV

Se o firmware ja estiver compilado e gravado, rode mais rapido assim:

```bash
python3 automator.py \
  testdata/sanity-model/model_quant.tflite \
  testdata/sanity-model/profiling_dataset \
  results.csv \
  --serial-device /dev/ttyACM0 \
  --arena-size 57344 \
  --skip-compile \
  --skip-deploy
```

## 7. Rodar a suite reduzida

O repositorio tambem tem um runner para reproduzir o experimento em formato de
suite:

```bash
source .venv/bin/activate
python python_scripts/experiments/run_benchmark_suite.py \
  testdata/experiments/image-classification-reduced-suite.json \
  ./results/reduced-suite.csv
```

Depois gere o relatorio:

```bash
python python_scripts/experiments/analyze_benchmark_suite.py \
  ./results/reduced-suite.csv \
  ./results/reduced-suite-report.md
```

Esse fluxo e melhor para apresentar reproducao, porque o manifesto JSON deixa
claro quais modelos, datasets, arenas e parametros foram usados.

## 8. Como a comunicacao serial funciona

O computador envia os bytes crus de uma entrada `float32`.

Na placa:

1. `serial_read()` bloqueia ate receber todos os bytes esperados
2. `start_timing()` inicia a medida
3. `model.run_inference()` executa a inferencia
4. `stop_timing()` calcula o tempo em microssegundos
5. `serial_write()` devolve 4 bytes com esse tempo

Importante: neste firmware, a placa devolve somente o tempo de inferencia. Ela
nao devolve a classe prevista nem o vetor de saida do modelo.

## 9. Como explicar a reproducao em uma apresentacao

Uma explicacao curta e direta:

> Para reproduzir o projeto de Bruno, eu uso a FRDM-MCXN947 como plataforma
> embarcada e o computador apenas como host de automacao. Primeiro preparo um
> modelo TensorFlow Lite quantizado e um conjunto de entradas em float32. Depois
> o script calcula caracteristicas do modelo, como MACs e tensor arena, gera o
> codigo C++ do TensorFlow Lite Micro, compila o firmware pelo MCUXpresso e grava
> a placa com LinkServer. Na execucao, o computador envia cada entrada pela
> serial, a placa executa a inferencia localmente e devolve o tempo medido em
> microssegundos. No final, o host salva um CSV com as metricas, permitindo
> comparar a latencia real medida na MCU com proxies como MACs, memoria e tempo
> no workstation.

## 10. Como explicar o papel da FRDM-MCXN947

A FRDM-MCXN947 nao treina o modelo. Ela tambem nao gera codigo. O papel dela e
executar a inferencia em condicao embarcada real.

O treinamento, a conversao para `.tflite`, a geracao de codigo, a compilacao e
a analise ficam no computador. A placa recebe apenas:

- o firmware ja compilado
- os bytes de entrada enviados pela serial

E devolve:

- o tempo real de inferencia medido dentro da MCU

Isso e essencial porque a pergunta do experimento nao e apenas "quantos MACs o
modelo tem", mas sim "quanto tempo esse modelo realmente leva em uma MCU".

## 11. O que precisa bater para dizer que reproduziu

Para considerar a reproducao valida, e preciso conseguir:

1. compilar o firmware sem erro
2. gravar a FRDM-MCXN947
3. abrir a serial correta
4. enviar pelo menos uma amostra `.bin`
5. receber 4 bytes de resposta por amostra
6. gerar um CSV com `mcu_avg_us`, `mcu_std_us`, `macs` e arena
7. repetir com mais de um modelo se o objetivo for calcular correlacao

Com apenas um modelo, o pipeline esta validado, mas correlacao ainda nao faz
sentido. Para correlacao, e necessario medir varias arquiteturas ou variacoes
de modelos.

## 12. Limitacoes que devem ser mencionadas

Algumas limitacoes importantes:

- o firmware atual mede latencia, mas nao valida a classe de saida pela serial
- a tensor arena pode precisar de ajuste manual se a estimativa automatica
  falhar
- resultados de desempenho dependem de runtime, compilador, flags e biblioteca
  TFLM usada
- uma suite com apenas uma entrada valida o pipeline, mas nao reproduz a analise
  estatistica completa
- para comparar com o trabalho original, e necessario medir varios modelos e
  gerar correlacoes

## 13. Resumo final

O sistema completo e um pipeline host + MCU:

```text
modelo .tflite + dataset .bin
        |
        v
scripts Python no computador
        |
        v
codigo C++ + model_data.h
        |
        v
MCUXpresso compila firmware
        |
        v
LinkServer grava FRDM-MCXN947
        |
        v
host envia entradas pela serial
        |
        v
FRDM executa TFLM e mede tempo
        |
        v
host salva CSV e gera relatorio
```

Essa e a forma pratica de explicar o uso do sistema do inicio ao fim para
reproduzir o experimento de Bruno com a `FRDM-MCXN947`.
