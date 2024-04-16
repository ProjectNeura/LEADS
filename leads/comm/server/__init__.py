from leads.comm.prototype import Callback
from leads.comm.server.server import Server


def create_server(port: int = 16900, callback: Callback = Callback()) -> Server:
    """
    Create a server service.
    :param port: the port on which the server listens
    :param callback: the callback methods
    :return: the server service
    """
    return Server(port, callback)


def start_server(target: Server = create_server(), parallel: bool = False) -> Server:
    """
    Starts the server service.
    :param target: the server service to start
    :param parallel: True: run in a separate thread; False: run in the caller thread
    :return: the server service
    """
    return target.start(parallel)
