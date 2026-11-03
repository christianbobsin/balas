# Checkpoint da medição de corrente — 2026-11-03

**Ponto de entrada para retomar o trabalho, aproximadamente em 2026-11-06.**
O usuário pediu para salvar o trabalho, fazer commit/push e continuar em cerca
de três dias. Não reiniciar a escolha do instrumento nem exigir refazer os
terminais dos shunts. Ler este checkpoint antes dos desenhos anteriores.

## Situação e objetivo

O objetivo é concluir o teste do instrumento e preparar a medição das placas
BALAS. O usuário dispõe de Arduino Due, placa TI INA180-181EVM completa com
os oito canais, shunts Caddock SR10 de 1 Ω e 0,1 Ω, multímetro, fios e
protoboard. Tem acesso eventual ao Fluke 5500A, mas esse acesso não é fácil;
não condicionar os testes iniciais ao Fluke ou à compra de outro shunt.

O usuário relatou não conseguir comprar outro shunt agora e não ter ferramentas
para fixar novos fios de sense nos metais. Não quer desmontar a adaptação ou
refazer as soldas para obter quatro conexões. Nas últimas instruções, **o Due
fornece apenas 3,3 V/GND pelo USB; A0 está desconectado e OUT é medido com o
multímetro**. Nenhuma aquisição pelo Due foi demonstrada nesta sessão.

A EVM completa existe, segundo o usuário, mas não estava com ele na última
mensagem. A mudança para o canal U1 ainda **não foi executada**.

## Componentes comuns disponíveis

| Componente | Quantidade |
| --- | ---: |
| Potenciômetro 5 kΩ | 1 |
| Potenciômetro 20 kΩ | 1 |
| Resistor 1 kΩ / ¼ W | 7 |
| Resistor 470 Ω / ¼ W | 2 |
| LED vermelho | 8 |

Os potenciômetros, resistores de 1 kΩ e LEDs não participam do ensaio de
shunt descrito neste checkpoint. O circuito 040 foi uma alternativa com
resistores comuns e não é o ponto atual de retomada.

## Adaptação dos shunts e fotos

O usuário colocou estanho nas partes metálicas e adicionou um fio por lado,
usando cada shunt como um componente de duas conexões externas. Não confundir
isso com quatro terminais independentes saindo para a protoboard.

No shunt de 0,1 Ω, um terminal metálico original se desprendeu do corpo após
aquecimento e foi recolocado por reaquecimento. Isso torna a estabilidade
incerta, mas não comprova que o shunt ficou inutilizado. Uma leitura na escala
de 200 Ω do multímetro também não permite confirmar 0,100 Ω ou sua tolerância.

As quatro fotos foram examinadas diretamente, com extração temporária do ZIP:

| Foto no ZIP | Observação visual |
| --- | --- |
| `20261102_174857.jpg` | Verso do shunt com fios amarelos; solda sobre as partes metálicas |
| `20261102_174904.jpg` | Marcação `SR10 0.10Ω 1%`, fios amarelos |
| `20261102_174919.jpg` | Verso do shunt com fios verdes; um fio aparece solto |
| `20261102_174929.jpg` | Marcação `SR10 1.00Ω 1%`, um fio verde solto |

Não foi observada ponte visível de estanho entre os dois lados do shunt de
0,1 Ω. A inspeção por foto não comprova integridade interna ou resistência
mecânica das junções. O de 1 Ω não está pronto como referência conectada:
nas fotos há um fio verde solto. Não exigir nova soldagem sem considerar
as limitações expressas pelo usuário.

Original preservado: [ZIP de fotos](imagens/shunts/Photos-1-001.zip).
As extrações temporárias não são necessárias para retomar; abrir novamente
o ZIP se precisar conferir as fotos. Não alterar o arquivo original.

## Circuito efetivamente orientado e ensaiado

Desenho atual: [041_teste_shunt_0p1_multimetro.png](imagens/041_teste_shunt_0p1_multimetro.png).
Editável: [SVG 041](imagens/041_teste_shunt_0p1_multimetro.svg).

```text
                R1 = 470 Ω
Due 3,3 V ──┬────[ R1 ]────┬── M ── fio amarelo ── SR10 0,1 Ω ── fio amarelo ── Due GND
            │              │
            └────[ R2 ]─────┘   R2 = outro 470 Ω, somente no segundo ensaio

INA VS   → Due 3,3 V
INA GND  → Due GND
INA IN+  → ponto M
INA IN−  → Due GND
INA OUT  → ponta vermelha do multímetro, borne V, tensão DC
COM      → Due GND
Due A0   → desconectado
```

Montar e mudar ligações com o USB desconectado. Não ligar o shunt sozinho
diretamente aos 3,3 V. R1/R2 limitam a corrente a aproximadamente 7/14 mA.
IN+ e IN− recebem sense; o caminho da carga não atravessa os bornes do INA.

Os resultados pressupõem o canal INA180A2 / U2, ganho nominal 50, conforme
identificado pelo usuário. Não houve foto da EVM confirmando as ligações
nos pontos de teste. Confirmar visualmente o canal quando a EVM estiver
disponível, antes de transferir conexões para U1.

## Medições relatadas pelo usuário

Valores fornecidos em conversa; não são leituras capturadas por instrumento
conectado ao computador. Horários individuais e modelo do multímetro não foram
informados. Os resultados não constituem certificado ou calibração completa.

| Condição / ponto | Valor informado | Observação |
| --- | ---: | --- |
| INA VS contra GND | 3,3 V | Alimentação |
| Queda no resistor de 470 Ω | 3,3 V | Valor arredondado informado pelo usuário |
| Entre INA IN+ e IN− | 2,5 mV | Inclui os pontos de conexão usados no ensaio |
| OUT, relato preliminar | 110 mV | Valor aproximado anterior à sequência abaixo |
| Diretamente entre partes metálicas do shunt | 0,6 mV | Mesmo ensaio com um 470 Ω, segundo relato |
| OUT, um resistor de 470 Ω — leitura 1 | **112,7 mV** | Escala 200 mV |
| OUT, dois resistores de 470 Ω em paralelo | **227,0 mV** | Escala 2 V; resolução exata não informada |
| OUT, voltando a um resistor de 470 Ω — leitura 3 | **114,4 mV** | Escala 200 mV |

Dados também em [CSV de medições](042_medicoes_relato_usuario.csv). Não preencher
os campos em branco da planilha de calibração do pacote 039 com previsões.

## Interpretação sustentada pelos resultados

Com 3,3 V e 470 Ω, a corrente aproximada é 7,02 mA. Com dois 470 Ω em paralelo
(235 Ω), é aproximadamente 14,04 mA. Essas estimativas usam valores nominais,
ignoram pequenas quedas adicionais e não substituem uma referência calibrada.

- A média das leituras de OUT com um resistor é **113,55 mV**.
- O dobro da média é **227,10 mV**, próximo dos **227,0 mV** informados.
- A diferença de retorno é **1,7 mV**, aproximadamente **1,5%** da média.
  Isso é uma comparação entre duas leituras, não uma precisão demonstrada.
- Houve mudança de escala no multímetro; sua resolução/exatidão devem entrar
  na avaliação. Não interpretar os dígitos de `227,0 mV` como resolução de 0,1 mV
  da escala de 2 V sem conferir o instrumento.

A resposta é aproximadamente proporcional nos dois níveis baixos ensaiados.
Não demonstra ainda estabilidade em corrente maior, calibração absoluta,
resposta a pulsos ou aquisição pelo Due.

A queda de 0,6 mV medida nos metais é próxima da ordem esperada para um shunt
de 0,1 Ω a 7 mA. A resolução do multímetro e a forma de contato impedem concluir
que o valor exato é 0,085 Ω ou que a tolerância original está preservada.
A diferença para os 2,5 mV medidos nas entradas sugere contribuição das conexões
externas e/ou dos pontos de referência. Não atribuir automaticamente toda a
diferença a um dano interno do SR10.

Assumindo ganho 50 e as correntes nominais, OUT implica uma resistência
**aparente fim a fim de aproximadamente 0,323 Ω**, ou transresistência de
aproximadamente 16,17 V/A. Isso inclui o conjunto e possíveis erros de
amplificação/offset; não é a resistência isolada do elemento SR10.
O desvio entre `2,5 mV × 50 = 125 mV` e os valores de OUT também não foi
isolado. Não tratar a estimativa como uma calibração concluída.

Com a montagem atual e ganho 50, extrapolar linearmente para 400 mA exigiria
cerca de **6,47 V em OUT**, impossível com alimentação de 3,3 V. Software
não recupera a informação perdida por saturação. Com essa estimativa, a
saída de 2 V ocorreria já perto de 124 mA, não de 400 mA.

## Decisão provisória: testar U1 / INA180A1, ganho 20

O usuário confirmou possuir a **EVM completa com os oito canais**. O manual
oficial identifica U1 como INA180A1, ganho 20. Isso permite investigar uma
faixa maior sem comprar outro shunt e sem modificar suas soldas.

Quando a EVM estiver disponível, desconectar USB/alimentação antes de
transferir as cinco conexões de U2 para U1. Manter o circuito de teste 041,
seu retorno de lado baixo, shunt e fios; não conectar ainda nenhuma placa BALAS.

| Sinal | U2 / A2 atual | U1 / A1 a testar |
| --- | --- | --- |
| VS / 3,3 V | TP211 | **TP111** |
| IN+ / M | TP212 | **TP112** |
| IN− / GND | TP213 | **TP113** |
| OUT / multímetro | TP214 | **TP114** |
| GND | TP215 | **TP115** |

Transferir a alimentação para o canal correto; não unir as saídas dos canais.
Identificar os pontos pela serigrafia/esquema, não pela posição ilustrativa
dos bornes nos desenhos anteriores. Não cortar a EVM.

Projeções usando apenas a razão nominal 20/50:

| Condição | OUT estimado no A1 |
| --- | ---: |
| Um resistor de 470 Ω | aproximadamente **45 mV** |
| Dois 470 Ω em paralelo | aproximadamente **91 mV** |
| 100 mA, extrapolação | aproximadamente **0,65 V** |
| 200 mA, extrapolação | aproximadamente **1,29 V** |
| 400 mA, extrapolação | aproximadamente **2,59 V** |

Os offsets dos canais não são idênticos. Não exigir igualdade exata com a
razão 20/50. As três últimas linhas são **projeções**, não ensaios aprovados.
Até agora, só foram testados aproximadamente 7 e 14 mA com o A2.

Além da saturação, verificar a queda de alimentação causada pelo conjunto:
0,323 Ω a 400 mA corresponde a cerca de **0,13 V**. Isso pode alterar o
funcionamento/consumo da placa medida e não é corrigido por simples ajuste
de corrente no software. Contatos podem mudar com corrente, temperatura e
movimentação; não extrapolar sua resistência baixa corrente como constante
sem teste. A potência total estimada nessa resistência a 400 mA é 52 mW,
mas essa conta não qualifica cada contato individual.

## Próxima ação exata ao retomar

1. Ler este checkpoint e conferir `git status`, preservando trabalho de firmware.
2. Confirmar que o usuário está com a EVM completa e identificar U1/TP111–TP115.
3. Repetir o ensaio 041 no U1, mantendo Due apenas como fonte e A0 desconectado.
4. Registrar OUT com um 470 Ω, dois em paralelo e retorno a um; usar a mesma
   escala do multímetro quando possível e registrar exatamente o visor/unidade.
5. Avaliar offset, repetição e razão de ganho entre U1 e U2 antes de fixar
   fatores de conversão. Não reaproveitar automaticamente o fator do A2.
6. Preparar um ensaio de corrente maior, com carga/fonte adequadas e verificação
   da queda nos contatos, antes de conectar NXP ou STM32 ou declarar 400 mA.
   O acesso ao Fluke é uma opção posterior, não um pré-requisito para o passo 3.
7. Somente depois integrar OUT ao A0 e calibrar a cadeia completa na montagem
   e no modo comum efetivamente usados. Não enviar nem substituir firmware
   nesta retomada sem verificar primeiro o trabalho preexistente.

O instrumento original usa medição no lado positivo da alimentação da placa;
o ensaio 041 é no retorno/GND. Mudar para a aplicação final pode alterar offset
por modo comum e introduzir caminhos paralelos por USB/debug. Verificar isso
antes de medir a placa real. A calibração não corrige corrente que bypassa o
shunt, saturação, contato intermitente ou perturbação da alimentação.

## Placas do projeto e faixas originalmente planejadas

Segundo a seção 10 do [documento 029](029_projeto_medicao_corrente_arduino_due.md):

| Placa | Ponto de acesso planejado | Faixa original |
| --- | --- | --- |
| NXP FRDM-MCXN947 | J24 / IDD_MCU | HIGH: 0,1 Ω, inicialmente até 400 mA |
| ST NUCLEO-H723ZG | JP4 / IDD | HIGH: 0,1 Ω, inicialmente até 400 mA |
| Nordic nRF52840 DK | P21 | LOW: 1 Ω, até 40 mA, somente após conferir picos em HIGH |

Essas são faixas do projeto, não consumos atuais medidos das placas.
A alternativa U1/ganho 20 ainda é experimental e não substitui automaticamente
as especificações e constantes do projeto original.

## Arquivos desta sequência

- 037: primeiro teste resistivo, com a adaptação por dois straps.
- 038: explicação da ligação Kelvin, alternativa com quatro conexões.
- 039: proposta com resistores comuns a adquirir e pacote de desenhos/partlist;
  não é o circuito atual nem evidência de montagem física.
- 040: teste usando os potenciômetros e resistores disponíveis; alternativa
  anterior, não usada nas medições deste checkpoint.
- **041: circuito atual efetivamente orientado e ensaiado, A2 + shunt 0,1 Ω.**
- **042: este checkpoint e CSV dos resultados relatados.**
- ZIP de fotos: evidência visual original dos dois shunts.

Não começar a retomada reenviando todos os PDFs ou impondo uma montagem nova.
O usuário pediu orientação prática, uma etapa por vez, com os componentes
disponíveis. Priorizar o desenho 041 e o teste do canal U1.

## Estado de Git e escopo de preservação

No início deste salvamento: branch `main`, remoto `origin` em
`git@github.com:christianbobsin/balas.git`, HEAD `7e24358`.
Havia alterações de firmware e ferramentas de aquisição anteriores ao ensaio:
`arduino-due/.gitignore`, `arduino-due/firmware/firmware.ino`, arquivos de
`acquisition`, exemplos de ADC, testes, requisitos e ferramentas Python.
Esses arquivos não foram criados/validados nesta conversa e devem permanecer
intocados e fora dos commits desta sessão.

Também havia uma pasta `039_circuitos_resistores_comuns/pacote_circuitos/`
com cópias extraídas do ZIP. Preservar localmente; os arquivos canônicos e
o ZIP já representam o pacote, sem necessidade de versionar duplicatas.

## Referências técnicas verificadas na conversa

- [TI: manual INA180-181EVM](https://www.ti.com/lit/ug/sbou183/sbou183.pdf),
  tabela de ganhos e esquema U1/U2.
- [TI: datasheet INA180](https://www.ti.com/lit/ds/symlink/ina180.pdf),
  alimentação, ganho, modo comum, offset e excursão de saída.
- [Caddock: Type SR](https://www.caddock.com/online-catalog/mrktg-lit/TypeSR.pdf),
  identificação C–S–S–C e condição de medição Kelvin.
- [Caddock AEN-0104](https://www.caddock.com/online-catalog/mrktg-lit/AEN0104.pdf),
  nota 5: perfil de soldagem da família SR não deve fazer o corpo exceder 219 °C;
  isso não é uma temperatura universal de regulagem do ferro.

## Limites da evidência

Não foram feitos nesta sessão: aquisição/calibração com o Due, teste do U1,
ensaio a 100/200/400 mA, teste com as três placas BALAS, medição calibrada da
resistência isolada, ensaio de estabilidade térmica, teste de pulsos ou operação
do Fluke. Nenhum desses itens deve ser reportado como aprovado.
