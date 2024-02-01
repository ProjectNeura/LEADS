#ifndef WHEELSPEEDSENSOR_H
#define WHEELSPEEDSENSOR_H


#include "Device.h"

#define BOUNCETIME 100

class WheelSpeedSensor : public Device<int> {
protected:
    long _t1, _t2;
    void (*_onUpdate)(int ws);

public:
    WheelSpeedSensor(int *const pins, void (*onUpdate)(int ws));
    void initialize();
    int read();
    String debug();
};


#endif // WHEELSPEEDSENSOR_H
