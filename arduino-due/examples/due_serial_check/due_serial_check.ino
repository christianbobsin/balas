// Teste de comunicacao pela porta Programming do Arduino Due.
// Monitor Serial: 115200 baud. Os bytes recebidos sao devolvidos ao PC.
// Este sketch substitui o firmware da placa; nao mede corrente.

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  Serial.println("DUE_SERIAL_CHECK_READY");
}

void loop() {
  while (Serial.available() > 0) {
    Serial.write(Serial.read());
  }

  static unsigned long lastHeartbeat = 0;
  static bool ledOn = false;
  const unsigned long now = millis();
  if (now - lastHeartbeat >= 1000) {
    lastHeartbeat = now;
    ledOn = !ledOn;
    digitalWrite(LED_BUILTIN, ledOn ? HIGH : LOW);
    Serial.print("DUE_OK millis=");
    Serial.println(now);
  }
}
