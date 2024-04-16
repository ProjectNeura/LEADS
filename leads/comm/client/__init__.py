from leads.comm.client.client import Client
from leads.comm.prototype import Callback


def create_client(port: int = 16900, callback: Callback = Callback()) -> Client:
    """
    Create a client service.
    :param port: the port to which the client connects
    :param callback: the callback methods
    :return: the client service
    """
    return Client(port, callback)


def start_client(server_address: str, target: Client = create_client(), parallel: bool = False) -> Client:
    """
    Starts the client service.
    :param server_address: the server address to which the client connects
    :param target: the client service to start
    :param parallel: True: run in a separate thread; False: run in the caller thread
    :return: the client service
    """
    return target.start(parallel, server_address=server_address)
