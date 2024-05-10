from os import getlogin as _get_login
from subprocess import run as _run

from leads_gui.system import get_system_kernel as _get_system_kernel


def configure_xws() -> None:
    if _get_system_kernel() != "linux":
        raise SystemError("Unsupported operating system")
    _run(("/usr/bin/xhost", f"+SI:localuser:{_get_login()}"))
