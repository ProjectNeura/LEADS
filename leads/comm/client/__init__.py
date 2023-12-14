from leads.comm.client.client import Client
from leads.comm.prototype import Callback


def create_client(port: int = 16900, callback: Callback = Callback()) -> Client:
    return Client(port, callback)


def start_client(server_address: str, target: Client = create_client(), parallel: bool = False) -> Client:
    return target.start(parallel, server_address=server_address)
