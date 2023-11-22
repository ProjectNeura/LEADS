from ..prototype import Entity, Connection


class Client(Entity):
    def run(self, server_address: str):
        self._socket.connect((server_address, self._port))
        with self._socket:
            self.callback.on_connect(self, connection := Connection(self, self._socket, (server_address, self._port)))
            self._stage(connection)

    def kill(self):
        self._socket.close()
