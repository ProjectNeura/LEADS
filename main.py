from sys import exit

from leads import MAIN_CONTROLLER, register_controller
from leads_gui.config import DEFAULT_CONFIG
from leads_emulation import SRWSin
from leads_vec.cli import main

if __name__ == '__main__':
    register_controller(MAIN_CONTROLLER, SRWSin(20, 60, acceleration=.008))
    c = main(DEFAULT_CONFIG)
    exit(c)
