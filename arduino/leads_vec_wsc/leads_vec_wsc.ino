#include "LEADS.h"

const int PIN_LFWSS[] = {2};
const int PIN_RFWSS[] = {3};
const int PIN_LRWSS[] = {4};
const int PIN_RRWSS[] = {5};
const int PIN_CRWSS[] = {6};

void reportWheelSpeed(String tag, float n) {
    Serial.print(tag + ":");
    Serial.print(n);
    Serial.print(";");
}

void lfwssOnUpdate(float ws) {
    reportWheelSpeed(LEFT_FRONT_WHEEL_SPEED_SENSOR, ws);
}

WheelSpeedSensor LFWSS(PIN_LFWSS, lfwssOnUpdate);

void setup() {
    Serial.begin(9600);
    LFWSS.initialize();
}

void loop() {
    LFWSS.read();
}
