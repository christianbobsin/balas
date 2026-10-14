# Diagnóstico do ADC do Due sem voltímetro

O registro enviado pelo usuário mostrou o firmware v0.1.0 executando, porém
com a média de A0 quase sempre próxima de 4095. Isso indica saturação ou uma
entrada próxima do limite superior; não identifica sozinho a causa nem a
tensão real no pino. O potenciômetro usado é de **20 kΩ**. Trocar seus dois
extremos apenas inverte o sentido do giro e não deveria eliminar a faixa.

O sketch de diagnóstico está em
[`arduino-due/examples/due_adc_diagnostic/due_adc_diagnostic.ino`](../arduino-due/examples/due_adc_diagnostic/due_adc_diagnostic.ino).
Ele permite testar GND, 3V3 e cinco níveis gerados pelo próprio DAC do Due.

## 1. Preparar a placa

**Desligue e retire qualquer fonte externa e desconecte o potenciômetro das
entradas.** Use somente a alimentação USB do Due para estes testes.
Nenhum firmware torna A0 tolerante a 5 V, e uma leitura de 4095 não distingue
3,3 V de uma sobretensão. Não conecte DAC0 a uma fonte externa ou a GND/3V3.

Este diagnóstico mantém A0 e A1 como entradas. Ele só habilita a saída DAC0
quando o comando `t` é enviado, e a desabilita depois do teste.

## 2. Gravar e abrir o monitor

No Arduino IDE, abra o `.ino` de diagnóstico, selecione **Arduino Due
(Programming Port)** e também a porta em **Ferramentas → Porta**, e faça
Upload. A gravação substitui temporariamente o firmware ADC v0.1.0.

Pelo terminal, a partir da raiz do repositório:

```bash
~/.local/bin/arduino-cli compile --fqbn arduino:sam:arduino_due_x_dbg \
  arduino-due/examples/due_adc_diagnostic
~/.local/bin/arduino-cli board list
~/.local/bin/arduino-cli upload --fqbn arduino:sam:arduino_due_x_dbg \
  --port /dev/ttyACM0 arduino-due/examples/due_adc_diagnostic
```

Confirme a porta detectada. Feche o Monitor Serial antes de gravar pelo CLI.
Depois, abra o monitor a **115200 baud**. Digite um comando de uma letra no
campo de envio e pressione Enter; qualquer opção usual de fim de linha é
aceita.

A versão v0.2 inicia com as leituras contínuas pausadas. Depois de ligar a
entrada a uma fonte válida, envie `r` para transmitir uma leitura a cada
500 ms:

```text
A0 min=... max=... media=... V_estimado=... saturadas=.../64
```

`saturadas` conta quantas das 64 leituras chegaram a 4095. A tensão continua
sendo uma estimativa com referência nominal de 3,3 V.

## 3. Primeiro teste: ponto conhecido em GND

Com a USB desconectada e o potenciômetro retirado, monte:

```text
Due GND ── resistor de 1 kΩ ── Due A0
```

Reconecte a USB, abra o monitor e envie **`g`**. A leitura deve ficar próxima
de zero. O programa imprime `TESTE_GND: COMPATIVEL` se a média for até 50
contagens. Esse limite é amplo e serve somente para verificar que a entrada
responde a um ponto baixo, não para medir precisão ou offset.

Se permanecer próxima de 4095, confira se o fio realmente chega a **A0**,
se o outro lado do resistor está em **GND** e se não há outra ligação na
entrada. Não altere os fios com a placa alimentada.

## 4. Teste automático usando o DAC

O Due oferece DAC0 e DAC1. O DAC possui uma faixa nominal de aproximadamente
**0,55 a 2,75 V**, dentro da faixa de entrada do ADC. Essa característica é
documentada pela [Arduino](https://store.arduino.cc/products/arduino-due).

Com a USB desconectada, retire o fio de GND do teste anterior e monte:

```text
Due DAC0 ── resistor de 1 kΩ ── Due A0
```

Não conecte outros componentes a DAC0 ou A0 durante o teste. Como ambos os
pinos pertencem à mesma placa, não é necessário um fio de GND adicional entre
eles. Use o pino marcado **DAC0**, não um pino digital com PWM.

Reconecte a USB, abra o monitor e envie **`t`**. O programa gera cinco
degraus e mede a resposta:

| Código enviado ao DAC | Tensão nominal aproximada | Código ADC nominal aproximado |
|---:|---:|---:|
| 0 | 0,55 V | 683 |
| 1024 | 1,10 V | 1365 |
| 2048 | 1,65 V | 2048 |
| 3072 | 2,20 V | 2731 |
| 4095 | 2,75 V | 3413 |

Portanto, **DAC com código zero não significa saída de 0 V** no Due.
Os valores esperados são calculados pelo modelo nominal:

```text
V_DAC ≈ Vref/6 + (codigo_DAC/4095) × (2×Vref/3)
codigo_ADC ≈ 4095/6 + (2×codigo_DAC/3)
```

O resultado tem o formato:

```text
dac_code,adc_expected,adc_mean,adc_min,adc_max,result
```

O diagnóstico considera cada nível compatível se a média estiver a até
**150 contagens** do valor esperado. Esse limite amplo foi escolhido para
detectar respostas grosseiramente incorretas, não deriva de uma homologação
metrológica e não é um critério de calibração. O teste não substitui a futura
referência externa nem comprova que todos os circuitos da placa estão íntegros.

Ao terminar, DAC0 é desabilitado. As leituras contínuas seguintes, com o fio
ainda conectado à saída desabilitada, não representam um degrau válido.
Na v0.1 elas continuavam aparecendo; na v0.2 o programa pausa essas leituras
para evitar confusão. Considere as cinco linhas do teste; envie `t` para
repeti-lo.

## 5. Comparar A0 com A1 se necessário

Se houver uma resposta inesperada em A0, desligue a USB e mova somente a ponta
do resistor que estava em A0 para **A1**, mantendo a outra ponta em DAC0.
Reconecte a USB, envie **`1`** para selecionar A1 e depois **`t`**. O programa
inicia em A0 após cada reinício, portanto a seleção de A1 precisa ser repetida.

Uma diferença entre os canais é evidência útil, mas ainda pode ser causada
por contato ou ligação incorreta. Não conclua que um pino queimou somente
com esse resultado.

## 6. Voltar ao potenciômetro de 20 kΩ

Se os cinco níveis variarem de modo compatível, desligue a USB e retire a
ligação com DAC0. Monte novamente:

```text
Due 3V3 ── um extremo do potenciômetro de 20 kΩ
Due GND ── outro extremo
Cursor central ── resistor de 1 kΩ ── Due A0
```

Reconecte, envie `r` e gire o potenciômetro lentamente de ponta a ponta. O diagnóstico
usa tracking maior do ADC, descarta oito conversões antes do lote e espaça
as leituras em 100 µs. A configuração é conservadora para este teste lento
com uma fonte resistiva; não comprova que a saturação anterior foi causada
pelo valor de 20 kΩ.

Se continuar no limite, mas o teste DAC responder aos cinco níveis, a
investigação passa para a ligação do potenciômetro, seus contatos e as linhas
da protoboard. Software não identifica sozinho um fio ligado ao ponto errado.

## 7. Comandos disponíveis

| Comando | Ação |
|---|---|
| `0` | Selecionar A0 |
| `1` | Selecionar A1 |
| `g` | Conferir leitura baixa; exige ligação manual a GND através de 1 kΩ |
| `h` | Conferir leitura alta; exige ligação manual a 3V3 através de 1 kΩ |
| `t` | Gerar os cinco níveis em DAC0 e conferir a entrada selecionada |
| `r` | Iniciar leituras contínuas com a entrada ligada a uma fonte válida |
| `?` | Mostrar ajuda |

O comando `h` verifica compatibilidade com média a partir de 4000 contagens;
esse resultado pressupõe conexão ao **3V3 do próprio Due**, nunca a 5 V.

## 8. Estado da validação

Em **2026-10-10**, o usuário confirmou a ligação **DAC0 → 1 kΩ → A0**, sem
potenciômetro, e enviou dois testes da v0.1: todos os cinco níveis foram
compatíveis em ambas as execuções. Uma terceira execução foi capturada
diretamente pelo computador em `/dev/ttyACM0`, a 115200 baud:

| Código DAC | ADC esperado | Média ADC capturada | Mínimo | Máximo |
|---:|---:|---:|---:|---:|
| 0 | 682,50 | 682,55 | 674 | 690 |
| 1024 | 1365,17 | 1366,78 | 1360 | 1377 |
| 2048 | 2047,83 | 2052,31 | 2040 | 2062 |
| 3072 | 2730,50 | 2736,34 | 2726 | 2746 |
| 4095 | 3412,50 | 3420,92 | 3414 | 3435 |

Registro: [`2026-10-10-dac0-a0-v0.1.log`](../arduino-due/validation/2026-10-10-dac0-a0-v0.1.log).

A0 respondeu de forma crescente e sem saturação nos cinco níveis aplicados.
Isso valida a resposta básica do caminho DAC0–resistor–A0 nessa faixa; não
constitui calibração com referência externa, teste de todas as entradas ou
validação do medidor de corrente. As leituras variáveis fora do teste foram
obtidas com DAC0 desabilitado e não avaliam uma fonte de tensão definida.

A v0.2 pausa as leituras na inicialização e após `t`. Compile com SAM core
1.6.12 e `arduino:sam:arduino_due_x_dbg`; envie `r` após remontar o teste do
potenciômetro. A captura acima corresponde à v0.1 que estava gravada na placa.

### Varredura com o diagnóstico v0.2

Na sequência, o usuário enviou um log com o cabeçalho **v0.2** e o comando
`r`, após a orientação de remontar o potenciômetro de 20 kΩ. O registro
mostra várias descidas e subidas entre os extremos, passando por níveis
intermediários:

| Ponto observado | Média ADC | Tensão estimada | Amostras em 4095 |
|---|---:|---:|---:|
| Extremo baixo | 0,28 | 0,0002 V | 0/64 |
| Ponto intermediário | 2056,97 | 1,6576 V | 0/64 |
| Próximo do extremo alto | 3973,84 | 3,2024 V | 0/64 |
| Extremo alto | 4095,00 | 3,3000 V | 64/64 |

A entrada deixou de permanecer travada no máximo. O comportamento é
compatível com uma varredura do potenciômetro entre GND e 3V3. A configuração
física desta etapa não foi inspecionada pelo computador; a interpretação
pressupõe a alimentação do potenciômetro pelo **3V3 do Due** conforme a
montagem indicada. O código máximo não confirma a tensão real nem exclui
sobretensão.

As diferenças entre mínimo e máximo durante a varredura podem incluir
movimento do cursor, ruído e variação de contato. Para avaliar estabilidade,
mantenha o cursor parado em um ponto intermediário por cerca de 10 segundos
e compare os lotes. Não estime precisão ou necessidade de filtragem apenas
com o cursor em movimento. Esta etapa valida a leitura básica com sinal
variável; a calibração externa e o circuito de corrente continuam pendentes.
