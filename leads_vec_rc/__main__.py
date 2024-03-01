from argparse import ArgumentParser as _ArgumentParser
from sys import exit as _exit

from uvicorn import run

from leads import L as _L, register_config as _register_config, load_config as _load_config
from leads_gui import get_system_platform as _get_system_platform, Config as _Config

if __name__ == "__main__":
    parser = _ArgumentParser(prog="LEADS VeC RC",
                             description="Lightweight Embedded Assisted Driving System VeC Remote Controller",
                             epilog="GitHub: https://github.com/ProjectNeura/LEADS")
    parser.add_argument("-r", "--register", choices=("systemd", "config"), default=None, help="service to register")
    parser.add_argument("-c", "--config", default=None, help="specified configuration file")
    parser.add_argument("-p", "--port", type=lambda p: int(p), default=8000, help="server port")
    args = parser.parse_args()
    if args.register == "systemd":
        if _get_system_platform() != "linux":
            _exit("Error: Unsupported operating system")
        from ._bootloader import create_service

        create_service()
        _L.info("Service registered")
    _register_config(config := _load_config(args.config, _Config) if args.config else None)
    from leads_vec_rc.cli import app

    run(app, host="0.0.0.0", port=args.port, log_level="warning")
