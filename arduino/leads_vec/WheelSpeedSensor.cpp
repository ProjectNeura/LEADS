#include "WheelSpeedSensor.h"

WheelSpeedSensor::WheelSpeedSensor(int *const pins) : Device<float>(pins) {
}

void WheelSpeedSensor::initialize() { pinMode(_pins[0], INPUT); }

float WheelSpeedSensor::read() {
    if (millis() - _t2 > BOUNCETIME && pulse(_pins[0])) {
        _t1 = _t2;
        _t2 = millis();
    }
    return 60 / (_t2 - _t1);
}
