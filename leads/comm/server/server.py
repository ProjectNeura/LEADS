from threading import Thread as _Thread

from leads.comm.prototype import Entity, Connection


class Server(Entity):
    _connections: list[Connection] = []
    _killed: bool = False

    def num_connections(self) -> int:
        return len(self._connections)

    def remove_connection(self, connection: Connection) -> None:
        try:
            self._connections.remove(connection)
        except ValueError:
            pass

    def run(self, max_connection: int = 1) -> None:
        self._killed = False
        self._socket.bind(("127.0.0.1", self._port))
        self._socket.listen(max_connection)
        self.callback.on_initialize(self)
        while not self._killed:
            socket, address = self._socket.accept()
            self.callback.on_connect(self, connection := Connection(self, socket, address,
                                                                    on_close=lambda c: self.remove_connection(c)))
            self._connections.append(connection)
            _Thread(target=self._stage, args=(connection,)).start()

    def broadcast(self, msg: bytes) -> None:
        for c in self._connections:
            try:
                c.send(msg)
            except IOError:
                self.remove_connection(c)

    def kill(self) -> None:
        self._killed = True
        self._socket.close()
        for connection in self._connections:
            connection.close()
