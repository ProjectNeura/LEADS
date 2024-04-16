from threading import Thread as _Thread
from typing import override as _override

from leads.comm.prototype import Entity, Connection
from leads.os import _thread_flags


class Server(Entity):
    """
    You should use `create_server()` and `start_server()` instead of directly calling any method.
    """
    _connections: list[Connection] = []

    def num_connections(self) -> int:
        """
        Get the number of active connections.
        :return: the number of connections
        """
        return len(self._connections)

    def remove_connection(self, connection: Connection) -> None:
        """
        Remove the connection from the list.
        :param connection: the connection to remove
        """
        try:
            self._connections.remove(connection)
        except ValueError:
            pass

    @_override
    def run(self, max_connection: int = 1) -> None:
        """
        Start listening for the connections and stage each connection in a new thread.
        :param max_connection: the maximum number of connections allowed at the same time
        """
        self._socket.bind(("0.0.0.0", self._port))
        self._socket.listen(max_connection)
        self._callback.on_initialize(self)
        while _thread_flags.active:
            socket, address = self._socket.accept()
            self._callback.on_connect(self, connection := Connection(self, socket, address,
                                                                     on_close=lambda c: self.remove_connection(c)))
            self._connections.append(connection)
            _Thread(target=self._stage, args=(connection,), daemon=True).start()

    def broadcast(self, msg: bytes) -> None:
        """
        Send the message to all connected clients.
        :param msg: the message to send
        """
        for c in self._connections:
            try:
                c.send(msg)
            except IOError:
                self.remove_connection(c)

    @_override
    def close(self) -> None:
        """
        Close all active connections.
        """
        self._socket.close()
        for connection in self._connections:
            connection.close()
