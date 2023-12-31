from os import chmod as _chmod
from os.path import abspath as _abspath


def create_service() -> None:
    _chmod(script := _abspath(__file__)[:-10] + "leads.service.sh", 777)
    with open("/etc/systemd/system/leads.service", "w") as f:
        f.write(f"""
        [Unit]
        Description=LEADS
        
        [Service]
        ExecStart=/bin/bash {script}
        
        [Install]
        WantedBy=graphical-session.target
        """)
