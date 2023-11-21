from .server import Server
from ..prototype import Callback


def create_server(port: int = 16400, callback: Callback = Callback()) -> Server:
    return Server(port, callback)


def start_server(target: Server = create_server(), parallel: bool = False) -> Server:
    return target.start(parallel)
