from leads.comm.prototype import Callback
from leads.comm.server.server import Server


def create_server(port: int = 16900, callback: Callback = Callback()) -> Server:
    return Server(port, callback)


def start_server(target: Server = create_server(), parallel: bool = False) -> Server:
    return target.start(parallel)
