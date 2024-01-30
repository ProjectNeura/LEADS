#ifndef WHEELSPEEDSENSOR_H
#define WHEELSPEEDSENSOR_H


#include "Device.h"

#define BOUNCETIME 20

class WheelSpeedSensor : public Device<float> {
protected:
    long _t1, _t2;

public:
    WheelSpeedSensor(int *const pins);
    void initialize();
    float read();
};


#endif // WHEELSPEEDSENSOR_H
