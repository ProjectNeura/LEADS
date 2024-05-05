from os.path import exists as _exists
from subprocess import run as _run
from threading import Thread as _Thread


def start_frpc() -> None:
    if not _exists("/usr/local/frp/frpc") or not _exists("/usr/local/frp/frpc.toml"):
        raise FileNotFoundError("frp not found")
    _Thread(name="frpc", target=_run, args=(("/usr/local/frp/frpc", "-c", "/usr/local/frp/frpc.toml"),),
            daemon=True).start()
