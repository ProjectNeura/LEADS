from threading import Thread as _Thread

from ..prototype import Entity, Connection


class Server(Entity):
    _connections: list[Connection] = []
    _killed: bool = False

    def run(self, max_connection: int = 1):
        self._killed = False
        self._socket.bind(("127.0.0.1", self._port))
        self._socket.listen(max_connection)
        self.callback.on_initialize(self)
        while not self._killed:
            socket, address = self._socket.accept()
            self.callback.on_connect(self, connection := Connection(self, socket, address))
            self._connections.append(connection)
            _Thread(target=self._stage, args=(connection,)).start()

    def broadcast(self, msg: bytes):
        for c in self._connections:
            c.send(msg)

    def kill(self):
        self._killed = True
        self._socket.close()
