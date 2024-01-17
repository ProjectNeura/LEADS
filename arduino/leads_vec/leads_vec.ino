const int PIN_LFWSS = 0;
const int PIN_RFWSS = 0;
const int PIN_LRWSS = 0;
const int PIN_RRWSS = 0;
const int PIN_MRWSS = 0;

void setup() {
  pinMode(PIN_LFWSS, INPUT);
  pinMode(PIN_RFWSS, INPUT);
  pinMode(PIN_LRWSS, INPUT);
  pinMode(PIN_RRWSS, INPUT);
  pinMode(PIN_MRWSS, INPUT);
  Serial.begin(9600);
}

boolean pulse(int pin) {
  return digitalRead(pin) == LOW
}

void loop() {
  if (pulse(PIN_LFWSS) Serial.println("A");
}
