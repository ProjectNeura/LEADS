from os.path import abspath as _abspath


def create_service() -> None:
    with open("/etc/systemd/system/leads.service", "w") as f:
        f.write(f"""
        [Unit]
        Description=LEADS
        After=default.target
        
        [Service]
        ExecStart={_abspath(__file__)[:-10] + "leads.service.sh"}
        
        [Install]
        WantedBy=default.target
        """)
