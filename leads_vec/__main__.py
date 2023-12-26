from sys import argv as _argv, exit as _exit

from leads_vec.config import load_config as _load_config, DEFAULT_CONFIG as _DEFAULT_CONFIG


def get_arg(args: list[str], name: str) -> str | None:
    for arg in args:
        if arg.startswith(name + "="):
            return arg[len(name) + 1:]


if __name__ == '__main__':
    try:
        from leads_emulation import SRWRandom as _Controller
    except ImportError:
        raise ImportError("At least one adapter has to be installed")
    cfg_arg = get_arg(_argv, "config")
    config = _load_config(cfg_arg) if cfg_arg else _DEFAULT_CONFIG
    from leads_vec.cli import main as _main

    _exit(_main(_Controller("main"), config))
