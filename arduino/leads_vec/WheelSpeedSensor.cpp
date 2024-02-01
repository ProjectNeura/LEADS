#include "WheelSpeedSensor.h"
#include "Algorithms.h"

WheelSpeedSensor::WheelSpeedSensor(int *const pins, OnUpdate onUpdate) : Device<int>(pins), _onUpdate(onUpdate) {
}

void WheelSpeedSensor::initialize() {
    pinMode(_pins[0], INPUT);
    _t1 = 0;
    _t2 = millis();
}

int getRPM(long t1, long t2) {
    return 60000 / (t2 - t1);
}

int WheelSpeedSensor::read() {
    if (millis() - _t2 > BOUNCETIME && pulseTriggered(_pins[0])) {
        _t1 = _t2;
        _t2 = millis();
        int r = getRPM(_t1, _t2);
        _onUpdate(r);
        return r;
    }
    return getRPM(_t1, _t2);
}

String WheelSpeedSensor::debug() {
    return String(_t1) + " " + String(_t2);
}
