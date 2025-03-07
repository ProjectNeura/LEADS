#ifndef BNO08X_H
#define BNO08X_H


#include "Adafruit_BNO08x_RVC.h"
#include "LEADS.h"

class BNO08x : public Accelerometer {
protected:
    Adafruit_BNO08x_RVC _rvc = Adafruit_BNO08x_RVC();
public:
    explicit BNO08x(OnAccelerometerUpdate onUpdate);
    void initialize(const ArrayList<String> &parentTags) override;
    Acceleration read() override;
};


#endif // BNO08X_H
