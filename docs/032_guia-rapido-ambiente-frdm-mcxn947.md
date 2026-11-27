# Guia rápido: ambiente da FRDM-MCXN947 no Linux

Este guia prepara um computador com **Ubuntu 22.04 ou 24.04, 64 bits
(`x86_64`)** para compilar, gravar e testar o projeto BALAS na placa
**FRDM-MCXN947**.

> Conecte a placa pelo conector **J17 (MCU-Link USB)** usando um cabo USB que
> transmita dados. Alguns cabos servem apenas para carregar e não funcionam.

## 1. O que será necessário

| Item | Para que serve | Onde obter |
|---|---|---|
| MCUXpresso IDE para Linux | Compilar o firmware | [Download oficial](https://www.nxp.com/mcuxpresso/ide/download) |
| LinkServer para Linux | Encontrar a placa e gravar o firmware | [Download oficial](https://www.nxp.com/design/software/development-software/mcuxpresso-software-and-tools-/linkserver-for-microcontrollers%3ALINKERSERVER) |
| SDK da FRDM-MCXN947 | Exemplos e bibliotecas da placa | [SDK Builder](https://mcuxpresso.nxp.com/) |
| Projeto BALAS | Código usado neste trabalho | [Repositório](https://github.com/christianbobsin/balas) |

A página oficial da placa e a documentação dos exemplos também estão
disponíveis em:

- [FRDM-MCXN947 — página da placa](https://www.nxp.com/design/design-center/development-boards-and-designs/FRDM-MCXN947)
- [Exemplos da FRDM-MCXN947 no MCUXpresso SDK](https://mcuxpresso.nxp.com/mcuxsdk/latest/html/boards/MCX/frdmmcxn947/index.html)

Não é necessário baixar o compilador Arm separadamente: o MCUXpresso IDE já
traz o toolchain usado pelo projeto.

## 2. Conferir o computador

Abra o aplicativo **Terminal** com `Ctrl+Alt+T` e execute:

```bash
uname -m
```

Este guia espera o resultado `x86_64`. Se aparecer `aarch64` ou `arm64`, não
instale os arquivos `x86_64`; será necessário escolher instaladores compatíveis
com a arquitetura do computador.

## 3. Instalar os pacotes básicos

Copie todo o bloco abaixo, cole no terminal e pressione `Enter`:

```bash
sudo apt update
sudo apt install -y \
  git curl wget unzip xz-utils tar \
  build-essential cmake ninja-build \
  libusb-1.0-0 udev \
  python3 python3-venv python3-pip \
  xxd picocom

sudo usermod -aG dialout "$USER"
```

Quando o terminal pedir a senha, digite a senha do seu usuário. Nada aparece
na tela enquanto a senha é digitada; isso é normal.

Depois do comando, **reinicie o computador** para aplicar a permissão da porta
serial.

## 4. Baixar e instalar as ferramentas da NXP

Os downloads da NXP podem exigir a criação de uma conta gratuita e a aceitação
da licença.

### 4.1 MCUXpresso IDE

1. Abra o [download do MCUXpresso IDE](https://www.nxp.com/mcuxpresso/ide/download).
2. Baixe o instalador para **Linux x86_64**. O nome costuma terminar em
   `.x86_64.deb.bin`.
3. Quando o download terminar, execute:

```bash
cd ~/Downloads
chmod +x mcuxpressoide-*.x86_64.deb.bin
sudo ./mcuxpressoide-*.x86_64.deb.bin
```

### 4.2 LinkServer

1. Abra a [página do LinkServer](https://www.nxp.com/design/software/development-software/mcuxpresso-software-and-tools-/linkserver-for-microcontrollers%3ALINKERSERVER).
2. Baixe **LinkServer installer Linux**. Para computador `x86_64`, não escolha
   a versão `Aarch64`.
3. Execute:

```bash
cd ~/Downloads
chmod +x LinkServer_*.x86_64.deb.bin
sudo ./LinkServer_*.x86_64.deb.bin
```

Se o instalador pedir para associar o LinkServer ao MCUXpresso IDE, escolha o
número do IDE instalado. Se o menu aparecer novamente depois da associação,
digite `q` para sair.

Adicione as duas ferramentas ao terminal:

```bash
grep -qxF 'export PATH="/usr/local/mcuxpressoide/ide:/usr/local/LinkServer:$PATH"' ~/.bashrc || \
  echo 'export PATH="/usr/local/mcuxpressoide/ide:/usr/local/LinkServer:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Confira a instalação:

```bash
test -x /usr/local/mcuxpressoide/ide/mcuxpressoide && echo "MCUXpresso: OK"
LinkServer -v
```

## 5. Baixar o SDK da placa

1. Abra o [MCUXpresso SDK Builder](https://mcuxpresso.nxp.com/).
2. Procure por `FRDM-MCXN947`.
3. Crie e baixe o SDK para **MCUXpresso IDE** no formato `.zip`.
4. Abra o MCUXpresso IDE.
5. Arraste o arquivo `SDK_*.zip` para a área **Installed SDKs** do IDE e confirme
   a importação.

O projeto BALAS já contém o código necessário da placa. O SDK completo é útil
principalmente para consultar e importar exemplos oficiais, como `hello_world`.

## 6. Baixar e preparar o projeto BALAS

No terminal:

```bash
cd ~/Documentos
git clone https://github.com/christianbobsin/balas.git
cd balas

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r docs/requirements.txt

cp .balas.env.example .balas.env
```

Se o repositório já foi baixado, não execute `git clone` novamente. Apenas entre
na pasta dele e continue a partir de `python3 -m venv .venv`.

## 7. Conectar e localizar a placa

Conecte o cabo USB em **J17 (MCU-Link USB)** e execute:

```bash
lsusb
LinkServer probes
ls /dev/ttyACM* 2>/dev/null
```

O esperado é:

- `LinkServer probes` listar uma placa ou probe MCU-Link;
- existir uma porta como `/dev/ttyACM0`.

Se a porta for diferente, por exemplo `/dev/ttyACM1`, edite `.balas.env`:

```bash
nano .balas.env
```

Adicione ou descomente esta linha, usando a porta encontrada:

```text
BALAS_SERIAL_PORT=/dev/ttyACM1
```

No `nano`, salve com `Ctrl+O`, pressione `Enter` e saia com `Ctrl+X`.

## 8. Compilar e gravar o firmware

Na raiz do projeto:

```bash
source .venv/bin/activate
BALAS_TARGET=nxp ./compile.sh
BALAS_TARGET=nxp ./deploy.sh
```

O primeiro comando deve gerar:

```text
cpp-project/tflite-test/Debug/tflite-test.axf
```

O segundo grava esse arquivo na FRDM-MCXN947. Se houver mais de uma placa
conectada, obtenha o serial com `LinkServer probes` e use:

```bash
BALAS_TARGET=nxp ./deploy.sh SERIAL_DO_PROBE
```

## 9. Teste rápido da porta serial

```bash
picocom -b 115200 /dev/ttyACM0
```

Para sair do `picocom`, pressione `Ctrl+A` e depois `Ctrl+X`.

## Problemas comuns

- **`Permission denied` na serial:** reinicie o computador e confirme que
  `groups` mostra o grupo `dialout`.
- **`LinkServer: comando não encontrado`:** execute `source ~/.bashrc` ou use
  `/usr/local/LinkServer/LinkServer -v`.
- **`LinkServer probes` não mostra a placa:** confirme que o cabo está em J17,
  troque o cabo USB e reconecte a placa.
- **O terminal não encontra o arquivo do instalador:** execute `ls ~/Downloads`
  e use a tecla `Tab` para completar o nome correto.
- **`/dev/ttyACM0` não existe:** rode `ls /dev/ttyACM*`; o número final pode ser
  diferente.

## Checklist final

```bash
test -x /usr/local/mcuxpressoide/ide/mcuxpressoide && echo "MCUXpresso: OK"
LinkServer -v
LinkServer probes
test -f cpp-project/tflite-test/Debug/tflite-test.axf && echo "Firmware: OK"
ls /dev/ttyACM* 2>/dev/null
```

Se todos os itens acima funcionarem, o ambiente básico da FRDM-MCXN947 está
pronto para usar com o projeto BALAS.
