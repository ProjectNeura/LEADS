from os.path import exists as _exists
from subprocess import run as _run


def start_frpc() -> None:
    if not _exists("/usr/local/frp/frpc") or not _exists("/usr/local/frp/frpc.toml"):
        raise FileNotFoundError("frp not found")
    _run(("/usr/local/frp/frpc", "-c", "/usr/local/frp/frpc.toml"))
