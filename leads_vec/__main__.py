from argparse import ArgumentParser as _ArgumentParser
from sys import exit as _exit

from leads_vec.config import load_config as _load_config, DEFAULT_CONFIG as _DEFAULT_CONFIG

if __name__ == '__main__':
    parser = _ArgumentParser(prog="LEADS",
                             description="Lightweight Embedded Assisted Driving System",
                             epilog="GitHub: https://github.com/ProjectNeura/LEADS")
    parser.add_argument("-c", "--config", nargs=1, default=None, help="configuration file")
    try:
        from leads_emulation import SRWRandom as _Controller
    except ImportError:
        raise ImportError("At least one adapter has to be installed")
    args = parser.parse_args()
    config = _load_config(args.config) if args.config else _DEFAULT_CONFIG
    from leads_vec.cli import main as _main

    _exit(_main(_Controller("main"), config))
