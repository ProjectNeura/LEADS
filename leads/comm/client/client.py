from ..prototype import Entity, Connection


class Client(Entity):
    _connection: Connection | None = None

    def run(self, server_address: str):
        self._socket.connect((server_address, self._port))
        self.callback.on_connect(self, connection := Connection(self, self._socket, (server_address, self._port)))
        self._connection = connection
        self._stage(connection)

    def send(self, msg: bytes):
        if self._connection is None:
            raise RuntimeError("Client must be running to perform this operation")
        self._connection.send(msg)

    def kill(self):
        self._socket.close()
