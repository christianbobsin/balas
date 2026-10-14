# Medidor de corrente com Arduino Due

Este diretório reúne o desenvolvimento do firmware do medidor de corrente do
BALAS. A arquitetura proposta está em
[docs/029_projeto_medicao_corrente_arduino_due.md](../docs/029_projeto_medicao_corrente_arduino_due.md):
Arduino Due, INA180-181EVM e dois shunts Kelvin de 1 Ω e 0,1 Ω.

O procedimento de instalação e teste está em
[docs/033_ambiente-arduino-due-linux.md](../docs/033_ambiente-arduino-due-linux.md).

## Firmware v0.1.0: validar o ADC

O sketch principal é [`firmware/firmware.ino`](firmware/firmware.ino). Ele lê A0
em 12 bits e publica mínimo, máximo, média e tensão estimada em CSV a 115200
baud. O procedimento, a lista de compras e os circuitos com e sem potenciômetro
estão em [docs/034_validacao-adc-arduino-due.md](../docs/034_validacao-adc-arduino-due.md).

O esquema está em [`hardware/adc_test.svg`](hardware/adc_test.svg). As montagens
usam somente 3V3 e GND do próprio Due, com um resistor de 1 kΩ em série com A0.

Na raiz do repositório:

```bash
arduino-cli compile --fqbn arduino:sam:arduino_due_x_dbg \
  --export-binaries arduino-due/firmware

arduino-cli upload --fqbn arduino:sam:arduino_due_x_dbg \
  --port /dev/ttyACM0 arduino-due/firmware
```

Selecione a porta detectada em `arduino-cli board list`. A gravação substitui
o exemplo serial anterior. Esta versão ainda usa `analogRead()` para testes
lentos, com referência nominal de 3,3 V; a aquisição por timer/PDC, o INA180 e
a calibração serão etapas posteriores.

## Diagnósticos

Para investigar uma leitura ADC que permanece em 4095, use o sketch separado
[`examples/due_adc_diagnostic/due_adc_diagnostic.ino`](examples/due_adc_diagnostic/due_adc_diagnostic.ino).
O [documento 035](../docs/035_diagnostico-adc-sem-voltimetro.md) explica o teste
sem voltímetro, com sinais gerados por DAC0 e ligação através de 1 kΩ. Esse
diagnóstico exige retirar o potenciômetro e a fonte externa durante o teste DAC.

- `examples/due_serial_check/due_serial_check.ino`: teste da porta Programming.
  Pisca o LED integrado, envia `DUE_OK millis=...` a cada segundo e devolve os
  bytes recebidos pelo PC, a 115200 baud.
- `tools/check_serial.py`: diagnóstico no PC que verifica três ecos e o
  heartbeat do exemplo. Requer Python com `pyserial`.

O exemplo verifica a comunicação; não lê o ADC. Não é necessário conectar
shunts ou a placa INA180 para executar este teste. O diagnóstico Python desta
seção espera o firmware de eco e não se aplica ao firmware ADC v0.1.0.

## Compilar e gravar o exemplo

Na raiz do repositório:

```bash
arduino-cli compile --fqbn arduino:sam:arduino_due_x_dbg \
  arduino-due/examples/due_serial_check

arduino-cli upload --fqbn arduino:sam:arduino_due_x_dbg \
  --port /dev/ttyACM0 arduino-due/examples/due_serial_check

python3 arduino-due/tools/check_serial.py --port /dev/ttyACM0
```

Confirme a porta com `arduino-cli board list` antes da gravação. A gravação
substitui o firmware que estiver na placa. No IDE, abra o arquivo `.ino`,
selecione **Arduino Due (Programming Port)** e a porta correspondente; abra o
Monitor Serial a **115200 baud** para observar as mensagens e testar o eco.

Os coeficientes de calibração do futuro medidor serão constantes do firmware,
persistidas na Flash por recompilação e regravação, conforme o documento 029.
