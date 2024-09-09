#include "Accelerometer.h"

void Accelerometer::initialize(const ArrayList<String> &parentTags) {
    Device<Acceleration>::initialize(parentTags);
    _rvc.begin(&Serial1);
}
Acceleration Accelerometer::read() {
    BNO08x_RVC_Data heading;
    Acceleration r = Acceleration();
    if (!_rvc.read(&heading)) return r;
    r.yaw = heading.yaw;
    r.pitch = heading.pitch;
    r.roll = heading.roll;
    r.forwardAcceleration = heading.x_accel;
    r.verticalAcceleration = heading.y_accel;
    r.lateralAcceleration = heading.z_accel;
    return r;
}