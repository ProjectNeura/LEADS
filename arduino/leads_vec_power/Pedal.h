#ifndef PEDAL_H
#define PEDAL_H


#include "Device.h"

class Pedal : public Device<float> {
protected:
    float _restValue, _maxValue;

public:
    VoltageSensor(const ArrayList<int> &pins, float restValue, float maxValue);
    void initialize(const ArrayList<String> &parentTags) override;
    float read() override;
};


#endif // PEDAL_H