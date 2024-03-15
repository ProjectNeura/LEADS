from os import chmod as _chmod
from os.path import abspath as _abspath


def create_service() -> None:
    _chmod(script := _abspath(__file__)[:-10] + "leads_vec_rc.service.sh", 777)
    with open("/etc/systemd/system/leads_vec_rc.service", "w") as f:
        f.write(
            "[Unit]\n"
            "Description=LEADS VeC RC\n"
            "[Service]\n"
            f"ExecStart=/bin/bash {script}\n"
            "[Install]\n"
            "WantedBy=default.target"
        )
