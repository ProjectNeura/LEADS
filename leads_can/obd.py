from typing import override as _override

from can import Message as _Message

from leads import DataContainer as _DataContainer
from leads_can.prototype import CANBus


class OBD2(CANBus):
    @_override
    def write(self, payload: _DataContainer) -> None:
        t = payload.time_stamp() * .001
        super().write(_Message(t, 0x00, data=str(payload.voltage).encode()))
        super().write(_Message(t, 0x01, data=str(payload.speed).encode()))
        super().write(_Message(t, 0x10, data=str(payload.front_wheel_speed).encode()))
        super().write(_Message(t, 0x11, data=str(payload.rear_wheel_speed).encode()))
        super().write(_Message(t, 0x20, data=str(payload.forward_acceleration).encode()))
        super().write(_Message(t, 0x21, data=str(payload.lateral_acceleration).encode()))
        super().write(_Message(t, 0x30, data=str(payload.mileage).encode()))
        super().write(_Message(t, 0x40, data=str(payload.gps_ground_speed).encode(),
                               is_error_frame=not payload.gps_valid))
        super().write(_Message(t, 0x41, data=str(payload.latitude).encode(),
                               is_error_frame=not payload.gps_valid))
        super().write(_Message(t, 0x42, data=str(payload.longitude).encode(),
                               is_error_frame=not payload.gps_valid))
        super().write(_Message(t, 0x50, data=str(payload.throttle).encode()))
        super().write(_Message(t, 0x51, data=str(payload.brake).encode()))
