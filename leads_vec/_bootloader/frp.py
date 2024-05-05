from os.path import exists as _exists
from subprocess import run as _run, DEVNULL as _DEVNULL
from threading import Thread as _Thread

from leads import L as _L


def start_frpc() -> None:
    if not _exists("/usr/local/frp/frpc") or not _exists("/usr/local/frp/frpc.toml"):
        raise FileNotFoundError("frp not found")

    def wrapper() -> None:
        _run(("/usr/local/frp/frpc", "-c", "/usr/local/frp/frpc.toml"), stdout=_DEVNULL, stderr=_DEVNULL)
        _L.error("frpc exits prematurely")

    _Thread(name="frpc", target=wrapper, daemon=True).start()
