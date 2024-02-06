from argparse import ArgumentParser as _ArgumentParser
from os import system as _system, chdir as _chdir
from os.path import abspath as _abspath
from sys import exit as _exit

from leads import L as _L
from leads_gui import get_system_platform as _get_system_platform

if __name__ == '__main__':
    parser = _ArgumentParser(prog="LEADS VeC RC",
                             description="Lightweight Embedded Assisted Driving System VeC Remote Controller",
                             epilog="GitHub: https://github.com/ProjectNeura/LEADS")
    parser.add_argument("-r", "--register", choices=("systemd", "config"), default=None, help="service to register")
    args = parser.parse_args()
    if args.register == "systemd":
        if _get_system_platform() != "linux":
            _exit("Error: Unsupported operating system")
        from ._bootloader import create_service

        create_service()
        _L.info("Service registered")
    _chdir(_abspath(__file__)[:-12])
    _system("uvicorn cli:app --reload")
