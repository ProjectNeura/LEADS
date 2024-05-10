from argparse import ArgumentParser as _ArgumentParser, BooleanOptionalAction as _BooleanOptionalAction
from importlib.metadata import version as _package_version, PackageNotFoundError as _PackageNotFoundError
from importlib.util import spec_from_file_location as _spec_from_file_location, module_from_spec as _module_from_spec
from os import getlogin as _get_login
from os.path import abspath as _abspath
from os.path import exists as _exists
from sys import exit as _exit, version as _version
from warnings import filterwarnings as _filterwarnings

from customtkinter import set_default_color_theme as _set_default_color_theme

from leads import register_controller as _register_controller, MAIN_CONTROLLER as _MAIN_CONTROLLER, \
    L as _L, load_config as _load_config, register_config as _register_config, reset as _reset
from leads.data_persistence import Dataset as _Dataset
from leads_gui import Config as _Config
from leads_gui.system import get_system_kernel as _get_system_kernel

if __name__ == "__main__":
    _filterwarnings("ignore")
    _MODULE_PATH = _abspath(__file__)[:-12]

    parser = _ArgumentParser(prog="LEADS VeC",
                             description="Lightweight Embedded Assisted Driving System VeC",
                             epilog="ProjectNeura: https://projectneura.org\n"
                                    "GitHub: https://github.com/ProjectNeura/LEADS")
    parser.add_argument("action", choices=("info", "replay", "run"))
    parser.add_argument("-c", "--config", default=None, help="specify a configuration file")
    parser.add_argument("-d", "--devices", default=f"{_MODULE_PATH}/devices.py",
                        help="specify a devices module")
    parser.add_argument("-r", "--register", choices=("systemd", "config", "reverse_proxy"), default=None,
                        help="register a service")
    parser.add_argument("-t", "--theme", default=None, help="specify a theme")
    parser.add_argument("-mfs", "--magnify-font-sizes", type=float, default=None, help="magnify font sizes by a factor")
    parser.add_argument("--emu", action=_BooleanOptionalAction, default=False, help="use emulator")
    parser.add_argument("--auto-mfs", action=_BooleanOptionalAction, default=False,
                        help="automatically magnify font sizes to match the original proportion")
    parser.add_argument("--xws", action=_BooleanOptionalAction, default=False, help="use X Window System")
    parser.add_argument("--ignore-import-error", action=_BooleanOptionalAction, default=False,
                        help="ignore `ImportError`")
    args = parser.parse_args()
    if args.action == "info":
        from leads_vec.__version__ import __version__
        from ._bootloader import frpc_exists as _frpc_exists

        leads_version = "Unknown"
        try:
            leads_version = _package_version("leads")
        except _PackageNotFoundError:
            _L.warn("Failed to retrieve package version (did you install through pip?)")
        _L.info(f"LEADS VeC",
                f"System Kernel: {_get_system_kernel().upper()}",
                f"Python Version: {_version}",
                f"User: {_get_login()}",
                f"`frpc` Available: {_frpc_exists()}",
                f"Module Path: {_MODULE_PATH}",
                f"LEADS Version: {leads_version}",
                f"LEADS VeC Version: {__version__}",
                sep="\n")
        _exit()
    if args.register == "systemd":
        from ._bootloader import create_service as _create_service

        _create_service()
        _L.info("Service registered")
        _L.info(f"Service script is located at \"{_MODULE_PATH}/_bootloader/leads_vec.service.sh\"")
    elif args.register == "config":
        if _exists("config.json"):
            r = input("\"config.json\" already exists. Overwrite? (y/N) >>>").lower()
            if r.lower() != "y":
                _exit("Error: Aborted")
        with open("config.json", "w") as f:
            f.write(str(_Config({})))
        _L.info("Configuration file saved to \"config.json\"")
    elif args.register == "reverse_proxy":
        from ._bootloader import start_frpc as _start_frpc

        _start_frpc()
        _L.info("`frpc` started")
    config = _load_config(args.config, _Config) if args.config else _Config({})
    _L.debug("Configuration loaded:", str(config))
    if t := args.theme:
        _set_default_color_theme(t)
    if f := args.magnify_font_sizes:
        config.magnify_font_sizes(f)
    if args.auto_mfs:
        config.auto_magnify_font_sizes()
    _register_config(config)
    if args.xws:
        from ._bootloader import configure_xws as _configure_xws

        _configure_xws()
        _L.info("X Window System configured")

    from leads_vec.cli import main

    if args.action == "replay":
        from leads_emulation.replay import ReplayController as _Controller

        _register_controller(_MAIN_CONTROLLER, _Controller(_Dataset(f"{config.data_dir}/main.csv")))
        _L.info("Replay started")
        _exit(main())

    try:
        if args.emu:
            raise SystemError("User specifies to use emulator")
        spec = _spec_from_file_location("_", args.devices)
        spec.loader.exec_module(_module_from_spec(spec))
    except (ImportError, SystemError) as e:
        _L.debug(repr(e))
        if isinstance(e, ImportError):
            if args.ignore_import_error:
                _L.debug(f"Ignoring import error: {repr(e)}")
                _exit(main())
            else:
                _L.warn(
                    f"Specified devices module ({args.devices}) is not available, using emulation module instead...")
        _reset()
        try:
            from leads_emulation import SinController as _Controller

            _register_controller(_MAIN_CONTROLLER, _Controller(0, 200, .05))
        except ImportError as e:
            _L.error(f"Emulator error: {repr(e)}")
            _exit(1)
    _exit(main())
