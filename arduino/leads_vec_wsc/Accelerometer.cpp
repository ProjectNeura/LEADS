#include "Accelerometer.h"

String Acceleration::toString() {
    return String(yaw) + "," + pitch + "," + roll + "," + forwardAcceleration + "," + lateralAcceleration + "," + verticalAcceleration;
}
Accelerometer::Accelerometer(OnAccelerometerUpdate onUpdate) : _onUpdate(onUpdate) {}
void Accelerometer::initialize(const ArrayList<String> &parentTags) {
    Device<Acceleration>::initialize(parentTags);
    Serial1.begin(115200);
    while (!Serial1) delay(10);
    if (!_rvc.begin(&Serial1)) delay(10);
}
Acceleration Accelerometer::read() {
    BNO08x_RVC_Data heading;
    Acceleration r = Acceleration();
    if (!_rvc.read(&heading)) return r;
    r.yaw = heading.yaw;
    r.pitch = heading.pitch;
    r.roll = heading.roll;
    r.forwardAcceleration = heading.x_accel;
    r.lateralAcceleration = heading.y_accel;
    r.verticalAcceleration = heading.z_accel;
    _onUpdate(r);
    return r;
}