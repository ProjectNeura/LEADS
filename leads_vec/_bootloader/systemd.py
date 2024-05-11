from os import chmod as _chmod, getlogin as _get_login, mkdir as _mkdir, environ as _environ
from os.path import abspath as _abspath, exists as _exists
from subprocess import run as _run, CalledProcessError as _CalledProcessError

from leads import L as _L
from leads_gui import Config as _Config
from leads_gui.system import get_system_kernel as _get_system_kernel


def is_service_active(name: str = "leads_vec") -> bool:
    try:
        _run(("systemctl", "is-active", f"{name}.service"), check=True)
        return True
    except _CalledProcessError:
        return False


def display_manager_service_name() -> str:
    for dm in ("gdm", "lightdm", "sddm", "xdm", "kdm"):
        if is_service_active(dm):
            return dm
    return "display-manager"


def register_leads_vec() -> None:
    if _get_system_kernel() != "linux":
        raise SystemError("Unsupported operating system")
    if is_service_active():
        raise SystemError("LEADS VeC is running")
    if not _exists("/usr/local/leads/config.json"):
        _L.debug("Config file not found. Creating \"/usr/local/leads/config.json\"...")
        if not _exists("/usr/local/leads"):
            _mkdir("/usr/local/leads")
        with open("/usr/local/leads/config.json", "w") as f:
            f.write(str(_Config({})))
    _chmod("/usr/local/leads/config.json", 0x644)
    _chmod(script := f"{_abspath(__file__)[:-10]}leads_vec.service.sh", 0o755)
    dm = display_manager_service_name()
    _L.debug(f"Detected display manager: {dm}")
    with open("/etc/systemd/system/leads_vec.service", "w") as f:
        f.write(
            "[Unit]\n"
            "Description=LEADS VeC\n"
            f"After={dm}.service\n"
            f"Requires={dm}.service\n"
            "[Service]\n"
            "Type=simple\n"
            f"User={(user := _get_login())}\n"
            f"Environment=\"USERNAME={user}\"\n"
            "Environment=\"DISPLAY=:0\"\n"
            f"Environment=\"XAUTHORITY={_environ["XAUTHORITY"]}\"\n"
            f"ExecStart=/bin/bash {script}\n"
            "[Install]\n"
            "WantedBy=graphical.target"
        )
