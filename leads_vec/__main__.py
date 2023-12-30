from argparse import ArgumentParser as _ArgumentParser
from os.path import exists as _exists
from sys import exit as _exit

from leads_dashboard import get_system_platform as _get_system_platform
from leads_vec.config import load_config as _load_config, DEFAULT_CONFIG as _DEFAULT_CONFIG

if __name__ == '__main__':
    parser = _ArgumentParser(prog="LEADS",
                             description="Lightweight Embedded Assisted Driving System",
                             epilog="GitHub: https://github.com/ProjectNeura/LEADS")
    parser.add_argument("-r", "--register", choices=("systemd", "config"), default=None, help="service to register")
    parser.add_argument("-c", "--config", default=None, help="specified configuration file")
    args = parser.parse_args()
    if args.register == "systemd":
        if _get_system_platform() != "linux":
            _exit("ERROR: Unsupported operating system")
        from ._bootloader import create_service

        create_service()
        _exit()
    elif args.register == "config":
        if _exists("config.json"):
            r = input("\"config.json\" already exists. Overwrite? (y/N) >>>").lower()
            if r.lower() != "y":
                _exit("ERROR: Aborted")
        with open("config.json", "w") as f:
            f.write(str(_DEFAULT_CONFIG))
        print("Configuration file saved to \"config.json\"")
        _exit()
    try:
        from leads_emulation import SRWRandom as _Controller
    except ImportError:
        raise ImportError("At least one adapter has to be installed")
    config = _load_config(args.config) if args.config else _DEFAULT_CONFIG
    from leads_vec.cli import main

    _exit(main(_Controller("main"), config))
