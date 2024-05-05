from os.path import exists as _exists
from subprocess import run as _run, PIPE as _PIPE
from threading import Thread as _Thread

from leads import L as _L


def start_frpc() -> None:
    if not _exists("/usr/local/frp/frpc") or not _exists("/usr/local/frp/frpc.toml"):
        raise FileNotFoundError("frp not found")

    def wrapper() -> None:
        r = _run(("/usr/local/frp/frpc", "-c", "/usr/local/frp/frpc.toml"), stdout=_PIPE, stderr=_PIPE)
        _L.error("`frpc` exits prematurely")
        _L.debug(f"Console output:\n{r.stdout.decode()}")

    _Thread(name="frpc", target=wrapper, daemon=True).start()
