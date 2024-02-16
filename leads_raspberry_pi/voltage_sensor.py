from leads import Device as _Device


class VoltageSensor(_Device):
    def __init__(self, pin: int) -> None:
        super().__init__(pin)
