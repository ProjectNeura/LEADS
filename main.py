from leads_emulation import SRWSin
from leads_vec.cli import main

if __name__ == '__main__':
    main(SRWSin("main", 20, 60, acceleration=.008), communication_server_address="127.0.0.1")
