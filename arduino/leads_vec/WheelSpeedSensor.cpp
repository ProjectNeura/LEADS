#include "WheelSpeedSensor.h"
#include "Algorithms.h"

WheelSpeedSensor::WheelSpeedSensor(int *const pins, OnUpdate onUpdate) : Device<float>(pins), _onUpdate(onUpdate) {
}

void WheelSpeedSensor::initialize() {
    pinMode(_pins[0], INPUT);
    _t1 = 0;
    _t2 = millis();
    _consecutive = false;
}

float getRPM(long t1, long t2) {
    return 60000.0 / (t2 - t1);
}

float WheelSpeedSensor::read() {
    if (pulseTriggered(_pins[0])) {
        if (!_consecutive) {
            _consecutive = true;
            _t1 = _t2;
            _t2 = millis();
            float r = getRPM(_t1, _t2);
            _onUpdate(r);
            return r;
        }
    } else _consecutive = false;
    return getRPM(_t1, _t2);
}

String WheelSpeedSensor::debug() {
    return String(_t1) + " " + String(_t2);
}
