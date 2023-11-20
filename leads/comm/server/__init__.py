from .server import Server


def create_server(port: int = 10000) -> Server:
    return Server(port)


def start_server(target: Server = create_server()):
    pass
