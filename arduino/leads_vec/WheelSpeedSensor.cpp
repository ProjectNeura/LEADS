#include "WheelSpeedSensor.h"

WheelSpeedSensor::WheelSpeedSensor(ArrayList<int> pins) : Device(pins) {}

void WheelSpeedSensor::initialize() { pinMode(_pins.get(0), INPUT); }

float WheelSpeedSensor::read() {
    if (millis() - _t2 > BOUNCETIME && pulse(_pins.get(0))) {
        _t1 = _t2;
        _t2 = millis();
    }
    return 60 / (_t2 - _t1);
}
