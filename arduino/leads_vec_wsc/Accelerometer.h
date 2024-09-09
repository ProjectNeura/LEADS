#include "Adafruit_BNO08x_RVC.h"
#include "LEADS.h"


struct Acceleration {
    float forwardAcceleration = 0, lateralAcceleration = 0, verticalAcceleration = 0;
};


class Accelerometer : public Device<Acceleration> {
protected:
    Adafruit_BNO08x_RVC _rvc = Adafruit_BNO08x_RVC();
public:
    void initialize(const ArrayList<String> &parentTags) override {
        Device<Acceleration>::initialize(parentTags);
        _rvc.begin(&Serial);
    }
    Acceleration read() override {
        BNO08x_RVC_Data heading;
        Acceleration r = Acceleration();
        if (!_rvc.read(&heading)) return r;
        r.forwardAcceleration = heading.x_accel;
        r.verticalAcceleration = heading.y_accel;
        r.lateralAcceleration = heading.z_accel;
    }
};
