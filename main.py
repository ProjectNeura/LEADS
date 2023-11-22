from leads_emulation import SRWRandom
from leads_vec.cli import main

if __name__ == '__main__':
    main(SRWRandom("main"), communication_server_address="127.0.0.1")
