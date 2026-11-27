// BALAS / Arduino Due -- v0.1.0: validacao de tensao no ADC.
// Porta Programming, Serial Monitor a 115200 baud.
// A entrada deve permanecer entre GND e 3V3; nunca aplicar 5 V.

#include <Arduino.h>

#if !defined(__SAM3X8E__)
#error "Este firmware foi preparado para o Arduino Due (SAM3X8E)."
#endif

constexpr uint8_t ADC_INPUT_PIN = A0;
constexpr uint16_t ADC_MAX_CODE = 4095;
constexpr uint16_t SAMPLES_PER_REPORT = 64;
constexpr uint32_t REPORT_INTERVAL_MS = 100;
// Valor nominal, nao uma referencia medida ou calibrada.
constexpr float ADC_REFERENCE_NOMINAL_V = 3.3f;
static_assert(ADC_INPUT_PIN >= A0 && ADC_INPUT_PIN <= A11,
              "Selecione uma entrada analogica entre A0 e A11.");

void setup() {
  Serial.begin(115200);
  pinMode(ADC_INPUT_PIN, INPUT);
  analogReadResolution(12);

  Serial.print(F("# BALAS Due ADC v0.1.0; entrada A"));
  Serial.print(ADC_INPUT_PIN - A0);
  Serial.println(F("; 12 bits; 115200 baud"));
  Serial.println(F("# Tensao estimada com referencia nominal de 3.3 V; sem calibracao"));
  Serial.println(F("t_ms,adc_min,adc_max,adc_mean,voltage_est_v,batch_us"));
}

void loop() {
  static uint32_t lastReportMs = 0;
  const uint32_t nowMs = millis();
  if (static_cast<uint32_t>(nowMs - lastReportMs) < REPORT_INTERVAL_MS) {
    return;
  }
  lastReportMs = nowMs;

  // Descarte uma conversao antes do lote. As amostras seguintes sao
  // consecutivas e bloqueantes; nao ha timer/PDC nem taxa fixa de captura.
  analogRead(ADC_INPUT_PIN);
  uint16_t minimum = ADC_MAX_CODE;
  uint16_t maximum = 0;
  uint32_t sum = 0;
  const uint32_t startUs = micros();
  for (uint16_t sample = 0; sample < SAMPLES_PER_REPORT; ++sample) {
    const uint16_t raw = analogRead(ADC_INPUT_PIN);
    sum += raw;
    if (raw < minimum) minimum = raw;
    if (raw > maximum) maximum = raw;
  }
  const uint32_t batchUs = micros() - startUs;
  const float mean = static_cast<float>(sum) / SAMPLES_PER_REPORT;
  const float voltage = mean * ADC_REFERENCE_NOMINAL_V / ADC_MAX_CODE;

  // Transmita somente apos concluir o lote de leituras.
  Serial.print(nowMs);
  Serial.print(',');
  Serial.print(minimum);
  Serial.print(',');
  Serial.print(maximum);
  Serial.print(',');
  Serial.print(mean, 2);
  Serial.print(',');
  Serial.print(voltage, 4);
  Serial.print(',');
  Serial.println(batchUs);
}
