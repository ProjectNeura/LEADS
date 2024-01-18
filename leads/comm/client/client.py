from leads.comm.prototype import Entity, Connection


class Client(Entity):
    _connection: Connection | None = None

    def run(self, server_address: str) -> None:
        self.callback.on_initialize(self)
        self._socket.connect((server_address, self._port))
        self.callback.on_connect(self, connection := Connection(self, self._socket, (server_address, self._port)))
        self._connection = connection
        self._stage(connection)

    def send(self, msg: bytes) -> None:
        if not self._connection:
            raise IOError("Client must be running to perform this operation")
        self._connection.send(msg)

    def kill(self) -> None:
        if self._connection:
            self._connection.close()
