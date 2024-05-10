from os import chmod as _chmod, getlogin as _get_login, mkdir as _mkdir
from os.path import abspath as _abspath, exists as _exists

from leads import L as _L
from leads_gui import Config as _Config
from leads_gui.system import get_system_kernel as _get_system_kernel


def create_service() -> None:
    if _get_system_kernel() != "linux":
        raise SystemError("Unsupported operating system")
    if not _exists("/usr/local/leads/config.json"):
        _L.debug("Config file not found. Creating \"/usr/local/leads/config.json\"...")
        _mkdir("/usr/local/leads")
        with open("/usr/local/leads/config.json", "w") as f:
            f.write(str(_Config({})))
    _chmod("/usr/local/leads/config.json", 777)
    _chmod(f"{(script := _abspath(__file__)[:-10])}leads_vec.service.sh", 777)
    with open("/etc/systemd/system/leads_vec.service", "w") as f:
        f.write(
            "[Unit]\n"
            "Description=LEADS VeC\n"
            "After=display-manager.service\n"
            "Requires=display-manager.service\n"
            "[Service]\n"
            "Type=simple\n"
            f"User={(user := _get_login())}\n"
            "Environment=\"DISPLAY=:0\"\n"
            f"Environment=\"XAUTHORITY=/home/{user}/.Xauthority\"\n"
            f"ExecStart=/bin/sh {script}\n"
            "[Install]\n"
            "WantedBy=graphical.target"
        )
