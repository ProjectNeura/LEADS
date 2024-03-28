#include "LEADS.h"

const int PIN_LFWSS[] = {2};
const int PIN_RFWSS[] = {3};
const int PIN_LRWSS[] = {4};
const int PIN_RRWSS[] = {5};
const int PIN_CRWSS[] = {6};

WheelSpeedSensor LFWSS(PIN_LFWSS, [](float ws) {returnFloat(LEFT_FRONT_WHEEL_SPEED_SENSOR, ws);});
WheelSpeedSensor RFWSS(PIN_RFWSS, [](float ws) {returnFloat(RIGHT_FRONT_WHEEL_SPEED_SENSOR, ws);});
WheelSpeedSensor LRWSS(PIN_LRWSS, [](float ws) {returnFloat(LEFT_REAR_WHEEL_SPEED_SENSOR, ws);});
WheelSpeedSensor RRWSS(PIN_RRWSS, [](float ws) {returnFloat(RIGHT_REAR_WHEEL_SPEED_SENSOR, ws);});
WheelSpeedSensor CRWSS(PIN_CRWSS, [](float ws) {returnFloat(CENTER_REAR_WHEEL_SPEED_SENSOR, ws);});

void setup() {
    Serial.begin(9600);
    LFWSS.initialize();
    RFWSS.initialize();
    LRWSS.initialize();
    RRWSS.initialize();
    CRWSS.initialize();
}

void loop() {
    LFWSS.read();
    RFWSS.read();
    LRWSS.read();
    RRWSS.read();
    CRWSS.read();
}
