from sys import exit

from leads_dashboard.config import DEFAULT_CONFIG
from leads_emulation import SRWSin
from leads_vec.cli import main

if __name__ == '__main__':
    c = main(SRWSin(20, 60, acceleration=.008), DEFAULT_CONFIG)
    exit(c)
