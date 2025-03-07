#include "BNO08x.h"

BNO08x::BNO08x(OnAccelerometerUpdate onUpdate) : Accelerometer(onUpdate) {}
void BNO08x::initialize(const ArrayList<String> &parentTags) {
    Accelerometer::initialize(parentTags);
    Serial1.begin(115200);
    while (!Serial1) delay(10);
    if (!_rvc.begin(&Serial1)) delay(10);
}
Acceleration BNO08x::read() {
    BNO08x_RVC_Data heading;
    Acceleration r = Acceleration();
    if (!_rvc.read(&heading)) return r;
    r.yaw = heading.yaw;
    r.pitch = heading.pitch;
    r.roll = heading.roll;
    r.forwardAcceleration = heading.y_accel;
    r.lateralAcceleration = heading.x_accel;
    r.verticalAcceleration = heading.z_accel;
    _onUpdate(r);
    return r;
}