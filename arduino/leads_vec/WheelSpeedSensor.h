#ifndef WHEELSPEEDSENSOR_H
#define WHEELSPEEDSENSOR_H


#include "Device.h"

#define BOUNCETIME 100

typedef void (*OnUpdate)(int ws);

class WheelSpeedSensor : public Device<int> {
protected:
    long _t1, _t2;
    OnUpdate _onUpdate;

public:
    WheelSpeedSensor(int *const pins, OnUpdate onUpdate);
    void initialize();
    int read();
    String debug();
};


#endif // WHEELSPEEDSENSOR_H
