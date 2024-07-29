#include "LEADS.h"  // LEADS>=1.1.0

const int PIN_LFWSS[] = {2};
const int PIN_RFWSS[] = {3};
const int PIN_LRWSS[] = {4};
const int PIN_RRWSS[] = {5};
const int PIN_CRWSS[] = {6};

Peer P{};
WheelSpeedSensor LFWSS{ArrayList<int>(PIN_LFWSS), [](float ws) {returnFloat(P, LEFT_FRONT_WHEEL_SPEED_SENSOR, ws);}};
WheelSpeedSensor RFWSS{ArrayList<int>(PIN_RFWSS), [](float ws) {returnFloat(P, RIGHT_FRONT_WHEEL_SPEED_SENSOR, ws);}};
WheelSpeedSensor LRWSS{ArrayList<int>(PIN_LRWSS), [](float ws) {returnFloat(P, LEFT_REAR_WHEEL_SPEED_SENSOR, ws);}};
WheelSpeedSensor RRWSS{ArrayList<int>(PIN_RRWSS), [](float ws) {returnFloat(P, RIGHT_REAR_WHEEL_SPEED_SENSOR, ws);}};
WheelSpeedSensor CRWSS{ArrayList<int>(PIN_CRWSS), [](float ws) {returnFloat(P, CENTER_REAR_WHEEL_SPEED_SENSOR, ws);}};

void setup() {
    P.initializeAsRoot();
    LFWSS.initializeAsRoot();
    RFWSS.initializeAsRoot();
    LRWSS.initializeAsRoot();
    RRWSS.initializeAsRoot();
    CRWSS.initializeAsRoot();
}

void loop() {
    LFWSS.read();
    RFWSS.read();
    LRWSS.read();
    RRWSS.read();
    CRWSS.read();
}
