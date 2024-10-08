#include "Adafruit_BNO08x_RVC.h"
#include "LEADS.h"


struct Acceleration {
    float yaw = 0, pitch = 0, roll = 0;
    float forwardAcceleration = 0, lateralAcceleration = 0, verticalAcceleration = 0;
    String toString();
};


typedef void (*OnAccelerometerUpdate)(Acceleration acceleration);


class Accelerometer : public Device<Acceleration> {
protected:
    Adafruit_BNO08x_RVC _rvc = Adafruit_BNO08x_RVC();
    const OnAccelerometerUpdate _onUpdate;
public:
    Accelerometer(OnAccelerometerUpdate onUpdate);
    void initialize(const ArrayList<String> &parentTags) override;
    Acceleration read() override;
};
