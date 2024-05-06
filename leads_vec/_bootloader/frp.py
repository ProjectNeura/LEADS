from os.path import exists as _exists
from subprocess import run as _run, PIPE as _PIPE
from threading import Thread as _Thread

from leads import L as _L
from leads_gui.system import get_system_kernel as _get_system_kernel


def start_frpc() -> None:
    path = "%AppData%/frp" if _get_system_kernel() == "windows" else "/usr/local/frp"

    if not _exists(f"{path}/frpc") or not _exists(f"{path}/frpc.toml"):
        raise FileNotFoundError("`frp` not found")

    def wrapper() -> None:
        r = _run((f"{path}/frpc", "-c", f"{path}/frpc.toml"), stdout=_PIPE, stderr=_PIPE)
        _L.error("`frpc` exits prematurely")
        _L.debug(f"Console output:\n{r.stdout.decode()}")

    _Thread(name="frpc", target=wrapper, daemon=True).start()
