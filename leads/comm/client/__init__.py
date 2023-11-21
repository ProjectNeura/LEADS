from .client import Client
from ..prototype import Callback


def create_client(port: int = 16400, callback: Callback = Callback()) -> Client:
    return Client(port, callback)


def start_client(server_address: str, target: Client = create_client()) -> Client:
    return target.start(server_address=server_address)
