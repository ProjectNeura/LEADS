from os.path import abspath as _abspath
from platform import system as _system


def get_system_kernel() -> str:
    return _system().lower()


_ASSETS_PATH: str = f"{_abspath(__file__)[:-9]}assets"
