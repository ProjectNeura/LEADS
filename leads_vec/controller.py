from leads import controller as _controller, MAIN_CONTROLLER as _MAIN_CONTROLLER
from leads_raspberry_pi import RaspberryPi4B as _RaspberryPi4B


@_controller(_MAIN_CONTROLLER)
class VeCController(_RaspberryPi4B):
    pass
