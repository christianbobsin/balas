# Contexto Atual

## Objetivo geral

Este repositorio implementa um fluxo para:

1. receber um modelo `.tflite` quantizado
2. gerar partes do codigo C++ embarcado para TensorFlow Lite Micro
3. compilar firmware para a placa NXP `FRDM-MCXN947` / MCU `MCXN947`
4. gravar o firmware na placa
5. enviar entradas por serial
6. medir o tempo de inferencia

O host de desenvolvimento e Linux. O firmware roda na MCU.

## Documentos lidos

Os documentos principais lidos para montar o contexto foram:

- `docs/projeto-visao-geral.md`
- `docs/frdm-mcxn947-ubuntu-24.04-primeiro-teste.md`

## O que foi entendido do projeto

- O repositorio contem scripts Python para automacao, geracao de codigo e profiling.
- O firmware principal esta em `cpp-project/tflite-test/`.
- O fluxo completo esperado passa por geracao de codigo, build, flash, serial e benchmarking.
- Ha varios problemas conhecidos no repositorio que ainda nao foram corrigidos nesta sessao, incluindo caminhos hardcoded e bugs em `input.h` / `output.h`.

## Estado atual do ambiente do usuario

Host atual do usuario:

- Ubuntu 24.04
- usuario: `christian`
- diretorio de trabalho do repositorio: `/home/christian/github/balas`

Ferramentas ja verificadas nesta sessao:

- `MCUXpresso IDE` instalado
- `LinkServer` instalado
- placa conectada via USB
- serial da placa presente em `/dev/ttyACM0`

## Instalacoes e verificacoes ja feitas

### 1. Bibliotecas de compatibilidade do MCUXpresso

Foram instaladas com sucesso:

- `libtinfo5`
- `libncurses5`
- `libncursesw5`

Observacao importante:

- apareceu um aviso final do `apt` sobre `_apt` e `Permissao negada`
- isso nao bloqueou a instalacao
- a instalacao foi considerada correta porque os pacotes foram configurados normalmente

### 2. MCUXpresso IDE

Confirmado presente em:

- `/usr/local/mcuxpressoide/ide/mcuxpressoide`

Observacao:

- ao rodar `mcuxpressoide --help >/dev/null`, apareceram mensagens `SLF4J` e avisos de jobs do Eclipse
- isso foi tratado como ruido do ambiente do IDE, nao como falha critica

### 3. LinkServer

O `LinkServer` foi instalado a partir do instalador no formato:

- `LinkServer_<versao>.x86_64.deb.bin`

Exemplo usado durante a sessao:

- `LinkServer_25.12.83.x86_64.deb.bin`

O instalador:

- pediu confirmacao de licenca com `y`
- pediu associacao com o IDE detectado
- foi necessario escolher `1`
- depois o menu apareceu novamente
- foi necessario digitar `q` para sair

Resultado validado:

- `/usr/local/LinkServer -> /usr/local/LinkServer_25.12.83`
- executavel principal em `/usr/local/LinkServer/LinkServer`

Importante:

- o nome correto do comando e `LinkServer`, com `L` e `S` maiusculos
- `linkserver` em minusculas falha no Linux
- o executavel nao ficou em `/usr/local/LinkServer/binaries/linkserver`

### 4. PATH

Foi ajustado no tutorial que o `PATH` correto do usuario deve incluir:

- `/usr/local/mcuxpressoide/ide`
- `/usr/local/LinkServer`

Importante:

- o `PATH` do `~/.bashrc` vale para o usuario normal
- `sudo` pode nao herdar esse mesmo `PATH`
- por isso, `sudo LinkServer ...` pode falhar mesmo quando `LinkServer ...` funciona

Quando usar `sudo`, o caminho absoluto confiavel e:

```bash
sudo /usr/local/LinkServer/LinkServer probes
```

## Estado atual da placa e do probe

Resultados observados:

- `lsusb` mostrou `NXP Semiconductors MCU-LINK FRDM-MCXN947 (r0E7) CMSIS-DAP V3.128`
- `/dev/ttyACM0` existe
- `LinkServer -v` funciona e mostra versao
- `LinkServer probes` em usuario normal retorna tabela vazia
- `sudo /usr/local/LinkServer/LinkServer probes` encontra a placa corretamente

Saida relevante confirmada:

```text
#  Description                                    Serial         Device    Board         Capabilities
---  ---------------------------------------------  -------------  --------  ------------  ----------------
1  MCU-LINK FRDM-MCXN947 (r0E7) CMSIS-DAP V3.128  EB04LLNGMJHMR  MCXN947   FRDM-MCXN947  DEBUG, VCOM, SIO
```

Conclusao atual:

- a placa esta conectada corretamente
- a instalacao do `LinkServer` esta correta
- o probe e reconhecido
- o problema restante e permissao de acesso ao probe no usuario normal

## Documentacao atualizada nesta sessao

O arquivo `docs/frdm-mcxn947-ubuntu-24.04-primeiro-teste.md` foi atualizado para:

- confirmar corretamente a instalacao das bibliotecas de compatibilidade
- explicar que o aviso final do `apt` nao e erro fatal
- separar a instalacao do `MCUXpresso IDE` da instalacao do `LinkServer`
- usar o padrao correto do instalador `LinkServer_<versao>.x86_64.deb.bin`
- explicar a etapa interativa de associacao com o IDE
- explicar que depois de associar o IDE e preciso digitar `q` para sair
- corrigir o caminho real do executavel para `/usr/local/LinkServer/LinkServer`
- corrigir todos os comandos para `LinkServer` com maiusculas
- explicar que `sudo` pode nao herdar o `PATH`
- explicar o diagnostico quando `LinkServer probes` funciona apenas com `sudo`

## Proximo passo recomendado

O proximo passo tecnico e resolver o acesso ao probe sem `sudo`.

Hipotese principal:

- falta permissao adequada de `udev` / `hidraw` para o `MCU-LINK` no usuario normal

Primeira linha de continuidade na proxima sessao:

1. inspecionar permissoes de `/dev/hidraw*`
2. identificar qual `hidraw` corresponde ao `MCU-LINK`
3. verificar se o instalador do `LinkServer` ou do `MCU-LINK_installer` trouxe regras de `udev`
4. instalar ou ajustar essas regras
5. validar novamente `LinkServer probes` sem `sudo`

## Comandos uteis para retomar

Verificar versao do LinkServer:

```bash
LinkServer -v
```

Verificar placa com usuario normal:

```bash
LinkServer probes
```

Verificar placa com privilegio:

```bash
sudo /usr/local/LinkServer/LinkServer probes
```

Verificar USB e serial:

```bash
lsusb
ls /dev/ttyACM* 2>/dev/null
ls -l /dev/hidraw*
```

## Resumo curto para retomada

Quando a proxima sessao comecar, o contexto essencial e:

- o IDE e o LinkServer ja estao instalados
- a documentacao ja foi corrigida em varios pontos
- a placa aparece no `lsusb` e a serial esta em `/dev/ttyACM0`
- o `LinkServer` so encontra o probe com `sudo`
- o proximo trabalho e corrigir permissao USB/udev para uso sem `sudo`
