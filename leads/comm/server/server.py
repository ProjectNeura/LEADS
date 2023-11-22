from threading import Thread as _Thread


from ..prototype import Entity, Connection


class Server(Entity):
    _threads: list[_Thread] = []
    _killed: bool = False

    def run(self, max_connection: int = 1, ):
        self._killed = False
        self._socket.bind(("127.0.0.1", self._port))
        self._socket.listen(max_connection)
        while not self._killed:
            socket, address = self._socket.accept()
            with socket:
                self.callback.on_connect(self, connection := Connection(self, socket, address))
                thread = _Thread(target=self._stage, args=(connection, ))
                self._threads.append(thread)
                thread.start()

    def kill(self):
        self._killed = True
        self._socket.close()
