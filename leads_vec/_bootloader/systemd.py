from os import chmod as _chmod
from os.path import abspath as _abspath


def create_service() -> None:
    _chmod(script := _abspath(__file__)[:-10] + "leads_vec.service.sh", 777)
    with open("/etc/systemd/system/leads_vec.service", "w") as f:
        f.write(
            "[Unit]"
            "Description=LEADS VeC"
            "After=display-manager.service"
            "Requires=display-manager.service"
            "[Service]"
            "Type=simple"
            "Environment=DISPLAY=:0"
            f"ExecStart=/bin/bash {script}"
            "[Install]"
            "WantedBy=graphical.target"
        )
