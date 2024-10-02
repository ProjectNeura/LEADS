from argparse import ArgumentParser as _ArgumentParser, BooleanOptionalAction as _BooleanOptionalAction
from importlib.metadata import version as _package_version, PackageNotFoundError as _PackageNotFoundError
from os import getlogin as _get_login
from os.path import abspath as _abspath
from sys import exit as _exit, version as _version
from warnings import filterwarnings as _filterwarnings

from leads import L as _L, register_controller as _register_controller, Controller as _Controller, \
    MAIN_CONTROLLER as _MAIN_CONTROLLER
from leads_gui.system import get_system_kernel as _get_system_kernel
from leads_vec.run import run

MODULE_PATH = _abspath(__file__)[:-13]


def parse_path(path: str | None) -> str | None:
    return path.replace(":INTERNAL", MODULE_PATH) if path else None


def __entry__() -> None:
    _filterwarnings("ignore")

    parser = _ArgumentParser(prog="LEADS VeC", description="Lightweight Embedded Assisted Driving System VeC",
                             epilog="Project Neura: https://projectneura.org\n"
                                    "GitHub: https://github.com/ProjectNeura/LEADS")
    parser.add_argument("action", choices=("info", "replay", "benchmark", "run"))
    parser.add_argument("-c", "--config", default=None, help="specify a configuration file")
    parser.add_argument("-d", "--devices", default=f"{MODULE_PATH}/devices.py", help="specify a devices module")
    parser.add_argument("-m", "--main", default=f"{MODULE_PATH}/cli.py", help="specify a main module")
    parser.add_argument("-r", "--register", choices=("systemd", "config", "reverse_proxy", "splash_screen"),
                        default=None, help="register a service")
    parser.add_argument("-mfs", "--magnify-font-sizes", type=float, default=1, help="magnify font sizes by a factor")
    parser.add_argument("--emu", action=_BooleanOptionalAction, default=False, help="use emulator")
    parser.add_argument("--auto-mfs", action=_BooleanOptionalAction, default=False,
                        help="automatically magnify font sizes to match the original proportion")
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
                f"Module Path: {MODULE_PATH}",
                f"LEADS Version: {leads_version}",
                f"LEADS VeC Version: {__version__}",
                sep="\n")
    else:
        match args.action:
            case "replay":
                args.devices = f"{MODULE_PATH}/replay.py"
                args.emu = False
                _L.debug("Replay mode enabled")
            case "benchmark":
                _register_controller(_MAIN_CONTROLLER, _Controller())
                args.devices = f"{MODULE_PATH}/benchmark.py"
                args.main = f"{MODULE_PATH}/benchmark.py"
                _L.debug("Benchmark mode enabled")
        _exit(run(parse_path(args.config), parse_path(args.devices), parse_path(args.main), args.register,
                  args.magnify_font_sizes, args.emu, args.auto_mfs, args.ignore_import_error))
    _exit()
