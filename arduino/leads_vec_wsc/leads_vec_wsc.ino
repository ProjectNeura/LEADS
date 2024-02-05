#include "LEADS.h"

const int PIN_LFWSS[] = {2};
const int PIN_RFWSS[] = {3};
const int PIN_LRWSS[] = {4};
const int PIN_RRWSS[] = {5};
const int PIN_MRWSS[] = {6};

void println(float n) {
    Serial.print(n);
    Serial.print(";");
}

void onUpdate(float ws) {
    println(ws);
}

WheelSpeedSensor LFWSS(PIN_LFWSS, onUpdate);

void setup() {
    Serial.begin(9600);
    LFWSS.initialize();
}

void loop() {
    LFWSS.read();
}
