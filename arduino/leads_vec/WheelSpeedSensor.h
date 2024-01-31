#ifndef WHEELSPEEDSENSOR_H
#define WHEELSPEEDSENSOR_H


#include "Device.h"

#define BOUNCETIME 20

class WheelSpeedSensor : public Device<int> {
protected:
    long _t1, _t2;

public:
    WheelSpeedSensor(int *const pins);
    void initialize();
    int read();
};


#endif // WHEELSPEEDSENSOR_H
