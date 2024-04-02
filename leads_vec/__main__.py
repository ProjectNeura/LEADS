from argparse import ArgumentParser as _ArgumentParser, BooleanOptionalAction as _BooleanOptionalAction
from os import mkdir as _mkdir, chmod as _chmod
from os.path import exists as _exists
from subprocess import run as _run
from sys import exit as _exit, version as _version

from leads import register_controller as _register_controller, MAIN_CONTROLLER as _MAIN_CONTROLLER, \
    L as _L, load_config as _load_config, register_config as _register_config, device as _device, \
    GPS_RECEIVER as _GPS_RECEIVER
from leads_gui import Config as _Config
from leads_gui.system import get_system_platform as _get_system_platform

if __name__ == "__main__":
    parser = _ArgumentParser(prog="LEADS VeC",
                             description="Lightweight Embedded Assisted Driving System VeC",
                             epilog="ProjectNeura: https://projectneura.org"
                                    "GitHub: https://github.com/ProjectNeura/LEADS")
    parser.add_argument("action", choices=("info", "run"))
    parser.add_argument("-r", "--register", choices=("systemd", "config"), default=None, help="service to register")
    parser.add_argument("-c", "--config", default=None, help="specified configuration file")
    parser.add_argument("--emu", action=_BooleanOptionalAction, default=False, help="use emulator")
    parser.add_argument("--xws", action=_BooleanOptionalAction, default=False, help="use X Window System")
    args = parser.parse_args()
    if args.action == "info":
        from leads_vec.__version__ import __version__

        _L.info("LEADS Version: " + __version__,
                "System Platform: " + _get_system_platform(),
                "Python Version: " + _version,
                sep="\n")
        _exit()
    if args.register == "systemd":
        if _get_system_platform() != "linux":
            _exit("Error: Unsupported operating system")
        if not _exists("/usr/local/leads/config.json"):
            _L.info("Config file not found. Creating \"/usr/local/leads/config.json\"...")
            _mkdir("/usr/local/leads")
            with open("/usr/local/leads/config.json", "w") as f:
                f.write(str(_Config({})))
            _L.info("Using \"/usr/local/leads/config.json\"")
        _chmod("/usr/local/leads/config.json", 777)
        from ._bootloader import create_service

        create_service()
        _L.info("Service registered")
    elif args.register == "config":
        if _exists("config.json"):
            r = input("\"config.json\" already exists. Overwrite? (y/N) >>>").lower()
            if r.lower() != "y":
                _exit("Error: Aborted")
        with open("config.json", "w") as f:
            f.write(str(_Config({})))
        _L.info("Configuration file saved to \"config.json\"")
    _register_config(config := _load_config(args.config, _Config) if args.config else _Config({}))
    _L.debug("Configuration loaded:", str(config))
    if args.xws:
        from os import getuid as _getuid
        from pwd import getpwuid as _getpwuid

        _L.info("Configuring X Window System...")
        _run(("/usr/bin/xhost", "+SI:localuser:" + _getpwuid(_getuid()).pw_name))
    try:
        if args.emu:
            raise AttributeError("User specifies to use emulator")
        from leads_vec.controller import _
    except (ImportError, AttributeError) as e:
        _L.debug(repr(e))
        if isinstance(e, ImportError):
            _L.warn("`leads_vec.controller` is not available, using emulation module instead...")
        try:
            if config.srw_mode:
                from leads_emulation import SRWSin as _Controller
            else:
                from leads_emulation import DRWSin as _Controller

            _register_controller(_MAIN_CONTROLLER, _Controller())
            from leads_emulation import GPSReceiver as _GPSReceiver


            @_device(_GPS_RECEIVER, _MAIN_CONTROLLER)
            class GPS(_GPSReceiver):
                pass
        except ImportError:
            raise ImportError("At least one adapter has to be installed")
    from leads_vec.cli import main

    _exit(main())
