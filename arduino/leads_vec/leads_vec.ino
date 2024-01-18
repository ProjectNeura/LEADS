const int PIN_LFWSS = 2;
const int PIN_RFWSS = 3;
const int PIN_LRWSS = 4;
const int PIN_RRWSS = 5;
const int PIN_MRWSS = 6;

void setup() {
    pinMode(PIN_LFWSS, INPUT);
    pinMode(PIN_RFWSS, INPUT);
    pinMode(PIN_LRWSS, INPUT);
    pinMode(PIN_RRWSS, INPUT);
    pinMode(PIN_MRWSS, INPUT);
}

bool pulse(int pin) { return digitalRead(pin) == LOW; }

void loop() {
    if (pulse(PIN_LFWSS))
        Serial.write("A\n;");
}
