# Arduino Due no Linux: instalação do IDE e teste de comunicação

Validação realizada em **09/10/2026**, no Ubuntu 24.04.5 LTS, arquitetura
`x86_64`. O Arduino Due foi identificado, recebeu o exemplo de comunicação e
respondeu ao PC pela porta Programming. O projeto do medidor será desenvolvido
em [`arduino-due/`](../arduino-due/README.md), conforme a
[proposta do documento 029](029_projeto_medicao_corrente_arduino_due.md).

## 1. Ambiente instalado

| Componente | Versão / localização |
|---|---|
| Arduino IDE | 2.3.10, ZIP oficial Linux x86_64 |
| Instalação do IDE | `~/.local/opt/arduino-ide_2.3.10_Linux_64bit/` |
| Comando do IDE | `~/.local/bin/arduino-ide` |
| Entrada no menu de aplicativos | `~/.local/share/applications/arduino-ide.desktop` |
| Arduino CLI incluído no IDE | 1.5.1; link em `~/.local/bin/arduino-cli` |
| Pacote da placa | `arduino:sam` 1.6.12, Arduino SAM Boards (32-bits ARM Cortex-M3) |
| Dados e ferramentas das placas | `~/.arduino15/` |
| Configuração do IDE | `~/.arduinoIDE/` |
| Python / pyserial usados no teste | 3.12.3 / 3.5, já disponíveis no computador |
| Logs e binários desta validação | `~/.cache/balas-arduino-setup/` |

A instalação foi feita na conta do usuário, sem `sudo`. O IDE também instalou
automaticamente o pacote AVR 1.8.8 na primeira abertura; o Due utiliza **SAM**.

## 2. Conectar e identificar a placa

Use um cabo USB de dados na porta **Programming**, próxima ao conector de
alimentação. Ela utiliza o ATmega16U2 como conversor USB–serial e corresponde a
`Serial` no sketch. A outra porta, **Native USB**, utiliza `SerialUSB` e exige
outra seleção de placa. Para este procedimento, use Programming.

Confira:

```bash
lsusb
ls -l /dev/ttyACM*
ls -l /dev/serial/by-id/
id -nG
```

Nesta validação, o resultado foi:

```text
ID 2341:003d Arduino SA Due Programming Port
/dev/ttyACM0, proprietário root, grupo dialout, permissões crw-rw----
```

O usuário já pertencia ao grupo `dialout`, e a porta abriu sem erro de permissão.
Em outro computador, se faltar esse grupo:

```bash
sudo usermod -aG dialout "$USER"
```

Encerre a sessão e entre novamente para aplicar a alteração. O número de
`ttyACM` pode mudar quando outras placas estiverem conectadas; confirme sempre
a identificação antes de gravar.

### Falha USB encontrada e resolvida

Antes da troca de cabo informada pelo usuário, o Due não aparecia no `lsusb`,
e nenhuma porta serial existia. O kernel registrou:

```text
device descriptor read/64, error -32
device not accepting address, error -71
unable to enumerate USB device
```

Após a troca, a placa foi identificada como `2341:003d` e criou `/dev/ttyACM0`.
O LED aceso confirmava alimentação, mas a identificação USB só funcionou após
essa mudança. Não foi necessário alterar drivers ou criar regras udev.

Para investigar uma recorrência, verifique cabo e contato e teste uma porta
direta do PC, sem hub. Consulte somente os registros recentes:

```bash
journalctl -k --since '-5 min' --no-pager
```

## 3. Instalar o Arduino IDE

Foi usada a distribuição ZIP oficial, disponível como alternativa portátil na
[documentação de instalação da Arduino](https://support.arduino.cc/hc/en-us/articles/360019833020-Download-and-install-Arduino-IDE).
Ela dispensa a montagem por FUSE exigida pelo AppImage.

Para reproduzir uma instalação nova da mesma versão:

```bash
mkdir -p ~/.cache/balas-arduino-setup ~/.local/opt ~/.local/bin
curl -fL --retry 2 \
  https://github.com/arduino/arduino-ide/releases/download/2.3.10/arduino-ide_2.3.10_Linux_64bit.zip \
  -o ~/.cache/balas-arduino-setup/arduino-ide_2.3.10_Linux_64bit.zip

printf '%s  %s\n' \
  cc8a0b01e763d4646b670ce70c1bc8c389a0fa14ab556dcc0749c03f475a7975 \
  "$HOME/.cache/balas-arduino-setup/arduino-ide_2.3.10_Linux_64bit.zip" \
  | sha256sum --check
```

O checksum acima foi obtido nos metadados da
[release oficial 2.3.10](https://github.com/arduino/arduino-ide/releases/tag/2.3.10)
e conferido antes da extração. Prossiga se aparecer `OK`:

```bash
unzip -q ~/.cache/balas-arduino-setup/arduino-ide_2.3.10_Linux_64bit.zip \
  -d ~/.local/opt

ln -s "$HOME/.local/opt/arduino-ide_2.3.10_Linux_64bit/resources/app/lib/backend/resources/arduino-cli" \
  ~/.local/bin/arduino-cli
```

### Abertura do IDE neste computador

A abertura padrão abortou com `FATAL:setuid_sandbox_host.cc`, indicando que o
helper `chrome-sandbox` não tinha proprietário root e modo 4755. A abertura
funcionou com `--no-sandbox`:

```bash
~/.local/opt/arduino-ide_2.3.10_Linux_64bit/arduino-ide --no-sandbox
```

Esse parâmetro desativa o sandbox do Chromium para o IDE. É uma limitação desta
instalação local; não foi alterada a política global do Ubuntu/AppArmor, nem
foram concedidos privilégios de root ao aplicativo.

O lançador instalado em `~/.local/bin/arduino-ide` utiliza esse parâmetro. Para
reproduzi-lo em uma instalação nova:

```bash
cat > ~/.local/bin/arduino-ide <<'EOF'
#!/bin/sh
exec "$HOME/.local/opt/arduino-ide_2.3.10_Linux_64bit/arduino-ide" --no-sandbox "$@"
EOF
chmod +x ~/.local/bin/arduino-ide
```

Neste computador também foi criada uma entrada **Arduino IDE** no menu de
aplicativos, apontando para esse lançador e para o ícone incluído no ZIP.
Para abrir pelo terminal, use `~/.local/bin/arduino-ide` ou `arduino-ide` se
`~/.local/bin` estiver no `PATH`.

## 4. Instalar o suporte ao Arduino Due

No IDE: abra o **Boards Manager**, procure **Arduino SAM Boards (32-bits ARM
Cortex-M3)** e instale. O pacote SAMD é destinado a outras placas.

Nesta sessão, o pacote foi instalado com o CLI incluído no IDE:

```bash
~/.local/bin/arduino-cli version
~/.local/bin/arduino-cli core update-index
~/.local/bin/arduino-cli core install arduino:sam@1.6.12
~/.local/bin/arduino-cli core list
~/.local/bin/arduino-cli board list
```

A placa detectada foi **Arduino Due (Programming Port)**, com o identificador
de compilação `arduino:sam:arduino_due_x_dbg` e porta `/dev/ttyACM0`.

## 5. Compilar, gravar e observar o exemplo

O código está em
[`arduino-due/examples/due_serial_check/due_serial_check.ino`](../arduino-due/examples/due_serial_check/due_serial_check.ino).
Ele pisca o LED integrado, envia `DUE_OK millis=...` a cada segundo e devolve
os bytes recebidos a **115200 baud**. A gravação substitui o firmware existente;
ela foi autorizada pelo usuário nesta sessão.

Na raiz do BALAS:

```bash
~/.local/bin/arduino-cli compile --fqbn arduino:sam:arduino_due_x_dbg \
  arduino-due/examples/due_serial_check

~/.local/bin/arduino-cli upload --fqbn arduino:sam:arduino_due_x_dbg \
  --port /dev/ttyACM0 arduino-due/examples/due_serial_check
```

No IDE, abra o `.ino`, selecione **Arduino Due (Programming Port)** e a porta
detectada, e clique em **Upload**. Abra o **Monitor Serial** a 115200 baud:
as mensagens `DUE_OK` devem aparecer, e um texto enviado deve retornar por eco.
Feche o Monitor Serial antes de usar o diagnóstico Python.

## 6. Confirmar a comunicação nos dois sentidos

O diagnóstico reutilizável está em
[`arduino-due/tools/check_serial.py`](../arduino-due/tools/check_serial.py).
Ele envia três mensagens com identificadores diferentes e verifica se cada
uma volta completa, além de conferir o heartbeat do firmware.

O script requer `pyserial`. Nesta máquina ele já estava disponível. Em outro
Ubuntu, pode ser instalado com `sudo apt install python3-serial`.

```bash
python3 arduino-due/tools/check_serial.py --port /dev/ttyACM0
```

Resultado esperado:

```text
TX: PING_DUE_0_<identificador>
RX: b'PING_DUE_0_<identificador>\n'
...
PASS: 3/3 ecos e heartbeat recebidos do Arduino Due
```

Abrir a porta pode reiniciar o SAM3X. Na primeira tentativa, o envio imediato
perdeu parte da mensagem durante esse reinício. O script aguarda 2,5 segundos
após a abertura e descarta dados antigos antes de testar o eco.

## 7. Resultado desta validação

- Identificação USB: `2341:003d`, Arduino Due Programming Port.
- Acesso serial: `/dev/ttyACM0` aberto sem erro de permissão.
- IDE: backend e interface iniciados; entrada do menu validada com
  `desktop-file-validate`.
- Compilação: sucesso, **11.036 bytes** de programa reportados pelo compilador.
- Gravação: dispositivo Atmel SMART `0x285e0a60` encontrado; **12.216 bytes**
  gravados em 48 páginas, com configuração de boot pela Flash e reinício.
- Execução física: mensagens `DUE_OK millis=...` recebidas do firmware.
- Comunicação PC → Due → PC: **três ecos completos**, com identificadores únicos.

O sketch de comunicação ficou gravado na placa. Esse resultado confirma o
ambiente de desenvolvimento e a comunicação serial; aquisição ADC/PDC,
front-end INA180, shunts e calibração de corrente ainda não foram testados.

Os registros completos estão em `~/.cache/balas-arduino-setup/`:
`ide-first-launch.log`, `ide-launch.log`, `core-update-index.log`,
`core-install-sam.log`, `compile-due-serial-check.log`,
`upload-due-serial-check.log` e `serial-check.log`.

## 8. Referências

- [Arduino Due — documentação oficial](https://docs.arduino.cc/hardware/due/).
- [Datasheet do Due — porta Programming e características elétricas](https://docs.arduino.cc/resources/datasheets/A000062-datasheet.pdf).
- [Instalação do Arduino IDE](https://support.arduino.cc/hc/en-us/articles/360019833020-Download-and-install-Arduino-IDE).
- [Boards Manager do IDE 2](https://docs.arduino.cc/software/ide-v2/tutorials/ide-v2-board-manager).
- [Release oficial do IDE 2.3.10](https://github.com/arduino/arduino-ide/releases/tag/2.3.10).
