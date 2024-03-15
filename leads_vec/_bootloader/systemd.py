from os import chmod as _chmod, getuid as _getuid
from os.path import abspath as _abspath
from pwd import getpwuid as _getpwuid


def create_service() -> None:
    _chmod(script := _abspath(__file__)[:-10] + "leads_vec.service.sh", 777)
    with open("/etc/systemd/system/leads_vec.service", "w") as f:
        f.write(
            "[Unit]\n"
            "Description=LEADS VeC\n"
            "After=display-manager.service\n"
            "Requires=display-manager.service\n"
            "[Service]\n"
            "Type=simple\n"
            f"User={(user := _getpwuid(_getuid()).pw_name)}\n"
            "Environment=\"DISPLAY=:0\"\n"
            f"Environment=\"XAUTHORITY=/home/{user}/.Xauthority\"\n"
            f"ExecStart=/bin/sh {script}\n"
            "[Install]\n"
            "WantedBy=graphical.target"
        )
