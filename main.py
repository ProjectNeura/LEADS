from leads_emulation import SRWSin
from leads_vec.cli import main
from leads_vec.config import DEFAULT_CONFIG

if __name__ == '__main__':
    main(SRWSin("main", 20, 60, acceleration=.008), DEFAULT_CONFIG)
