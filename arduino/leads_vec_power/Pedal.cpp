#include "Pedal.h"

Pedal::Pedal(const ArrayList<int> &pins, float restValue, float maxValue) : Device<float>(pins), _restValue(restValue), _maxValue(maxValue) {}

Pedal::initialize(const ArrayList<String> &parentTags) {
    Device<float>::initialize(parentTags);
    pinMode(_pins[0], INPUT);
}

float Pedal::read() { return ((float) analogRead(_pins[0]) / 1023 - _restValue) / _maxValue; }
