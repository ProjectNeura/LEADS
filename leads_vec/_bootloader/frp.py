from subprocess import run as _run


def start_frpc() -> None:
    _run("/usr/local/frp/frpc -c /usr/local/frpc.toml")
