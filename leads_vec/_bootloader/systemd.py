from os import chmod as _chmod, getlogin as _get_login, makedirs as _mkdirs
from os.path import abspath as _abspath, exists as _exists

from leads import L as _L
from leads_gui import Config as _Config
from leads_gui.system import get_system_kernel as _get_system_kernel


def register_leads_vec() -> None:
    if _get_system_kernel() != "linux":
        raise SystemError("Unsupported operating system")
    if not _exists("/usr/local/leads/config.json"):
        _L.debug("Config file not found. Creating \"/usr/local/leads/config.json\"...")
        if not _exists("/usr/local/leads"):
            _mkdirs("/usr/local/leads")
        with open("/usr/local/leads/config.json", "w") as f:
            f.write(str(_Config({})))
    _chmod("/usr/local/leads/config.json", 0x644)
    _chmod(script := f"{_abspath(__file__)[:-10]}leads-vec.service.sh", 0o755)
    if not _exists(user_systemd := f"/home/{_get_login()}/.config/systemd/user"):
        _L.debug(f"User Systemd not found. Creating \"{user_systemd}\"...")
        _mkdirs(user_systemd)
    with open(f"{user_systemd}/leads-vec.service", "w") as f:
        f.write(
            "[Unit]\n"
            "Description=LEADS VeC\n"
            "After=graphical-session.target\n"
            "[Service]\n"
            "Type=simple\n"
            f"ExecStart=/bin/bash {script}\n"
            f"Restart=always\n"
            f"RestartSec=1s\n"
            "[Install]\n"
            "WantedBy=default.target"
        )
    if not _exists(user_systemd_wants := f"{user_systemd}/default.target.wants"):
        _L.debug(f"User Systemd broken. Creating \"{user_systemd_wants}\"...")
        _mkdirs(user_systemd_wants)
    _chmod(user_systemd_wants, 0o777)
