#include "WheelSpeedSensor.h"
#include "Algorithms.h"

const int PIN_LFWSS[] = {2};
const int PIN_RFWSS[] = {3};
const int PIN_LRWSS[] = {4};
const int PIN_RRWSS[] = {5};
const int PIN_MRWSS[] = {6};

WheelSpeedSensor LFWSS(PIN_LFWSS);

void setup() {
    Serial.begin(9600);
    LFWSS.initialize();
}

void loop() {
    Serial.println(LFWSS.read());
}
