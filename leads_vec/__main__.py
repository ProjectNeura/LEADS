from importlib.util import find_spec as _find_spec
from sys import argv as _argv, exit as _exit

from leads_vec.config import load_config as _load_config, DEFAULT_CONFIG as _DEFAULT_CONFIG


def get_arg(args: list[str], name: str) -> str | None:
    for arg in args:
        if arg.startswith(name + "="):
            return arg[len(name) + 1:]


if __name__ == '__main__':
    if not _find_spec("dearpygui"):
        raise ImportError("Please install `dearpygui` to run this module\n>>> pip install dearpygui")
    if not _find_spec("keyboard"):
        raise ImportError("Please install `keyboard` to run this module\n>>> pip install keyboard")
    try:
        from leads_emulation import SRWRandom as _Controller
    except ImportError:
        raise ImportError("At least one adapter has to be installed")
    cfg_arg = get_arg(_argv, "config")
    config = _load_config(cfg_arg) if cfg_arg else _DEFAULT_CONFIG

    if "--remote" in _argv:
        from leads_vec.remote import remote as _main

        _exit(_main(config))
    else:
        from leads_vec.cli import main as _main

        _exit(_main(_Controller("main"), config))
