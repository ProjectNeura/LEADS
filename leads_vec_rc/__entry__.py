from argparse import ArgumentParser as _ArgumentParser

from uvicorn import run as _run

from leads import register_config as _register_config, load_config as _load_config
from leads_gui import Config as _Config


def __entry__() -> None:
    parser = _ArgumentParser(prog="LEADS VeC RC",
                             description="Lightweight Embedded Assisted Driving System VeC Remote Controller",
                             epilog="GitHub: https://github.com/ProjectNeura/LEADS")
    parser.add_argument("-c", "--config", default=None, help="specify a configuration file")
    parser.add_argument("-p", "--port", type=int, default=8000, help="specify a server port")
    args = parser.parse_args()
    _register_config(_load_config(args.config, _Config) if args.config else _Config({}))
    from leads_vec_rc.cli import app

    _run(app, host="0.0.0.0", port=args.port, log_level="warning")