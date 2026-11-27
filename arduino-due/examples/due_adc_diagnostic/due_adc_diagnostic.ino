// Diagnostico do ADC do Due sem voltimetro.
// Porta Programming, 115200 baud. Nunca aplicar 5 V nas entradas.
// O teste DAC exige: DAC0 -> resistor 1 kOhm -> entrada selecionada.
// Retire o potenciometro e qualquer fonte externa antes de enviar 't'.

#include <Arduino.h>

#if !defined(__SAM3X8E__)
#error "Este diagnostico requer o Arduino Due (SAM3X8E)."
#endif

constexpr uint16_t SAMPLE_COUNT = 64;
constexpr float ADC_MAX = 4095.0f;
constexpr float NOMINAL_REFERENCE_V = 3.3f;
// Limite amplo para diagnosticar resposta a degraus, nao para calibracao.
constexpr float DAC_ADC_TOLERANCE = 150.0f;
uint8_t inputPin = A0;
bool continuousReadings = false;

struct Reading {
  uint16_t minimum;
  uint16_t maximum;
  uint16_t clipped;
  float mean;
};

Reading readInput() {
  // Aumente o tracking do ADC para o teste lento com fontes resistivas.
  ADC->ADC_MR = (ADC->ADC_MR & ~ADC_MR_TRACKTIM_Msk) | ADC_MR_TRACKTIM(15);
  for (uint8_t discard = 0; discard < 8; ++discard) {
    analogRead(inputPin);
    delayMicroseconds(100);
  }
  Reading result = {4095, 0, 0, 0.0f};
  uint32_t sum = 0;
  for (uint16_t sample = 0; sample < SAMPLE_COUNT; ++sample) {
    const uint16_t value = analogRead(inputPin);
    sum += value;
    if (value < result.minimum) result.minimum = value;
    if (value > result.maximum) result.maximum = value;
    if (value == 4095) ++result.clipped;
    delayMicroseconds(100);
  }
  result.mean = static_cast<float>(sum) / SAMPLE_COUNT;
  return result;
}

void printReading(const Reading &reading) {
  Serial.print('A');
  Serial.print(inputPin - A0);
  Serial.print(F(" min="));
  Serial.print(reading.minimum);
  Serial.print(F(" max="));
  Serial.print(reading.maximum);
  Serial.print(F(" media="));
  Serial.print(reading.mean, 2);
  Serial.print(F(" V_estimado="));
  Serial.print(reading.mean * NOMINAL_REFERENCE_V / ADC_MAX, 4);
  Serial.print(F(" saturadas="));
  Serial.print(reading.clipped);
  Serial.println(F("/64"));
}

void printHelp() {
  Serial.println(F("\n# Due ADC diagnostico v0.2; 115200 baud"));
  Serial.println(F("# ADC com tracking maior; amostragem lenta; entrada nunca acima de 3V3"));
  Serial.println(F("0: selecionar A0; 1: selecionar A1; ?: mostrar ajuda"));
  Serial.println(F("g: conferir GND (ligue GND -> 1k -> entrada antes do comando)"));
  Serial.println(F("h: conferir 3V3 (ligue 3V3 -> 1k -> entrada antes do comando)"));
  Serial.println(F("t: testar DAC0 -> 1k -> entrada, SEM potenciometro/fonte externa"));
  Serial.println(F("r: iniciar leituras continuas; exige entrada ligada a uma fonte valida"));
  Serial.println(F("# Desligue a USB para mudar fios; envie o comando apos religar."));
  Serial.println(F("# A leitura saturada nao distingue 3.3 V de uma sobretensao."));
  Serial.println(F("# Ao iniciar e apos t, leituras continuas ficam pausadas."));
}

void checkEndpoint(bool high) {
  const Reading reading = readInput();
  printReading(reading);
  const bool compatible = high ? reading.mean >= 4000.0f : reading.mean <= 50.0f;
  Serial.print(high ? F("TESTE_3V3: ") : F("TESTE_GND: "));
  Serial.println(compatible ? F("COMPATIVEL") : F("FORA_DA_FAIXA_ESPERADA"));
  Serial.println(F("# Esse resultado pressupoe que o fio foi ligado ao ponto indicado."));
}

void runDacTest() {
  continuousReadings = false;
  const uint16_t levels[] = {0, 1024, 2048, 3072, 4095};
  bool allCompatible = true;
  Serial.println(F("\n# TESTE DAC0: somente DAC0 -> 1k -> entrada; sem outra conexao"));
  Serial.println(F("# O DAC do Due gera aproximadamente 0.55 a 2.75 V, nao 0 a 3.3 V."));
  Serial.println(F("dac_code,adc_expected,adc_mean,adc_min,adc_max,result"));
  for (uint8_t index = 0; index < sizeof(levels) / sizeof(levels[0]); ++index) {
    const uint16_t code = levels[index];
    analogWrite(DAC0, code);
    delay(20);
    const Reading reading = readInput();
    // DAC: Vref/6 + codigo/4095 * (2*Vref/3); ADC: codigo/Vref * 4095.
    const float expected = ADC_MAX / 6.0f + 2.0f * code / 3.0f;
    const float difference = reading.mean - expected;
    const bool compatible = difference >= -DAC_ADC_TOLERANCE &&
                            difference <= DAC_ADC_TOLERANCE;
    allCompatible = allCompatible && compatible;
    Serial.print(code);
    Serial.print(',');
    Serial.print(expected, 2);
    Serial.print(',');
    Serial.print(reading.mean, 2);
    Serial.print(',');
    Serial.print(reading.minimum);
    Serial.print(',');
    Serial.print(reading.maximum);
    Serial.print(',');
    Serial.println(compatible ? F("COMPATIVEL") : F("FORA_DA_FAIXA"));
  }
  // Termine desabilitando a saida analogica, sem manter o ultimo nivel.
  DACC->DACC_CHDR = DACC_CHDR_CH0;
  pinMode(DAC0, INPUT);
  Serial.println(allCompatible
      ? F("RESULTADO: cinco niveis compativeis com a resposta nominal DAC->ADC.")
      : F("RESULTADO: resposta fora da faixa; conferir fio, entrada e DAC antes de concluir dano."));
  Serial.println(F("# Verificacao de coerencia, nao calibracao nem teste completo do chip."));
  Serial.println(F("# DAC0 desabilitado; leituras continuas pausadas. Envie t para repetir."));
  Serial.println(F("# Para medir outra fonte, desligue a USB, refaca os fios e depois envie r."));
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  analogWriteResolution(12);
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);
  pinMode(DAC0, INPUT);
  printHelp();
}

void loop() {
  while (Serial.available() > 0) {
    const char command = Serial.read();
    switch (command) {
      case '0': inputPin = A0; Serial.println(F("Entrada selecionada: A0")); break;
      case '1': inputPin = A1; Serial.println(F("Entrada selecionada: A1")); break;
      case 'g': case 'G': checkEndpoint(false); break;
      case 'h': case 'H': checkEndpoint(true); break;
      case 't': case 'T': runDacTest(); break;
      case 'r': case 'R':
        continuousReadings = true;
        Serial.println(F("Leituras continuas iniciadas; confirme a fonte ligada a entrada."));
        break;
      case '?': printHelp(); break;
      case '\r': case '\n': case ' ': break;
      default: Serial.println(F("Comando desconhecido; envie ? para ajuda.")); break;
    }
  }
  static uint32_t lastReportMs = 0;
  const uint32_t nowMs = millis();
  if (continuousReadings && static_cast<uint32_t>(nowMs - lastReportMs) >= 500) {
    lastReportMs = nowMs;
    printReading(readInput());
  }
}
