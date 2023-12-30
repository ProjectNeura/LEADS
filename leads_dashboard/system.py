from platform import system as _system


def get_system_platform() -> str:
    return _system().lower()
