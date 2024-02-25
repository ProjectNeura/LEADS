from os.path import abspath as _abspath
from platform import system as _system


def get_system_platform() -> str:
    return _system().lower()


_ASSETS_PATH: str = _abspath(__file__)[:-9] + "assets"
