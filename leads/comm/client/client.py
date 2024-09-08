from typing import override as _override

from leads.comm.prototype import Entity, Connection, Callback


class Client(Entity):
    """
    You should use `create_client()` and `start_client()` instead of directly calling any method.
    """

    def __init__(self, port: int, callback: Callback, separator: bytes) -> None:
        """
        :param port: the port to which the client connects
        :param callback: the callback interface
        :param separator: the symbol that splits the stream into messages
        """
        super().__init__(port, callback)
        self._connection: Connection | None = None
        self._separator: bytes = separator

    @_override
    def run(self, server_address: str) -> None:
        """
        Establish a connection and stage it.
        :param server_address: the server address to which the client connects
        """
        self._callback.on_initialize(self)
        self._socket.connect((server_address, self._port))
        self._callback.on_connect(self, connection := Connection(self._socket, (server_address, self._port),
                                                                 separator=self._separator))
        self._connection = connection
        self._stage(connection)

    def send(self, msg: bytes) -> None:
        """
        Send the message to the server.
        :param msg: the message to send
        :exception IOError: no connection
        """
        if not self._connection:
            raise IOError("Client must be running to perform this operation")
        self._connection.send(msg)

    @_override
    def close(self) -> None:
        """
        Close the connection.
        """
        if self._connection:
            self._connection.close()
