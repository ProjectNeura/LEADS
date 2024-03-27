from abc import abstractmethod as _abstractmethod, ABCMeta as _ABCMeta
from socket import socket as _socket, AF_INET as _AF_INET, SOCK_STREAM as _SOCK_STREAM, \
    gethostbyname_ex as _gethostbyname_ex, gethostname as _gethostname
from threading import Lock as _Lock, Thread as _Thread
from typing import Self as _Self, Callable as _Callable, override as _override

from leads.callback import CallbackChain
from leads.os import _threads_life_flag


def my_ip_addresses() -> list[str]:
    return [ip for ip in _gethostbyname_ex(_gethostname())[2] if not ip.startswith("127.")]


class Service(metaclass=_ABCMeta):
    def __init__(self, port: int) -> None:
        """
        :param port: the port on which the service listens
        """
        self._lock: _Lock = _Lock()
        self._port: int = port
        self._socket: _socket = _socket(_AF_INET, _SOCK_STREAM, proto=0)
        self._main_thread: _Thread | None = None

    def port(self) -> int:
        return self._port

    @_abstractmethod
    def run(self, *args, **kwargs) -> None:  # real signature unknown
        """
        Override this method to define the specific workflow.
        :param args: args
        :param kwargs: kwargs
        """
        raise NotImplementedError

    def _run(self, *args, **kwargs) -> None:
        """
        This method is equivalent to `Service.run()`. It leaves a middle layer for possible features in subclasses.
        :param args: args passed to `Service.run()`
        :param kwargs: kwargs passed to `Service.run()`
        """
        self.run(*args, **kwargs)

    def _register_process(self, *args, **kwargs) -> None:
        """
        Register the multithread worker.
        :param args: args passed to `Service.run()`
        :param kwargs: kwargs passed to `Service.run()`
        """
        self._lock.acquire()
        if self._main_thread:
            raise RuntimeWarning("A service can only run once")
        try:
            self._main_thread = _Thread(name="service" + str(hash(self)), target=self._run, daemon=True, args=args,
                                        kwargs=kwargs)
        finally:
            self._lock.release()

    def _parallel_run(self, *args, **kwargs) -> None:
        """
        This method is similar to `Service._run()` except that it runs the workflow in a child thread.
        :param args: args passed to `Service.run()`
        :param kwargs: kwargs passed to `Service.run()`
        """
        self._register_process(*args, **kwargs)
        self._main_thread.start()

    def start(self, parallel: bool = False, *args, **kwargs) -> _Self:
        """
        This is the publicly exposed interface to start the service.
        :param parallel: True: main thread not blocked; False: main thread blocked
        :param args: args passed to `Service.run()`
        :param kwargs: kwargs passed to `Service.run()`
        :return: self
        """
        try:
            return self
        finally:
            if parallel:
                self._parallel_run(*args, **kwargs)
            else:
                self._run(*args, **kwargs)

    @_abstractmethod
    def kill(self) -> None:
        raise NotImplementedError


class ConnectionBase(metaclass=_ABCMeta):
    def __init__(self, service: Service, remainder: bytes, separator: bytes) -> None:
        """
        :param service: the service to which it belongs
        :param remainder: message remain from last connection
        """
        self._service: Service = service
        self._remainder: bytes = remainder
        self._separator: bytes = separator

    def use_remainder(self) -> bytes:
        if (i := self._remainder.find(self._separator)) < 0:
            msg = self._remainder
            self._remainder = b""
        elif i != len(self._remainder) - 1:
            msg = self._remainder[:i]
            self._remainder = self._remainder[i + 1:]
        else:
            msg = self._remainder[:-1]
            self._remainder = b""
        return msg

    def with_remainder(self, msg: bytes) -> bytes:
        if (i := msg.find(self._separator)) != len(msg) - 1:
            self._remainder = msg[i + 1:]
            return msg[:i]
        return msg[:-1]

    @_abstractmethod
    def closed(self) -> bool:
        """
        :return: True: the socket is closed; False: the socket is active
        """
        raise NotImplementedError

    @_abstractmethod
    def receive(self) -> bytes | None:
        """
        :return: message in bytes or None
        """
        raise NotImplementedError

    @_abstractmethod
    def send(self, msg: bytes) -> None:
        """
        :param msg: message in bytes
        """
        raise NotImplementedError

    def disconnect(self) -> None:
        """
        Request disconnection.
        """
        self.send(b"disconnect")

    @_abstractmethod
    def close(self) -> None:
        """
        Directly close the socket.
        """
        raise NotImplementedError


class Connection(ConnectionBase):
    def __init__(self, service: Service, socket: _socket, address: tuple[str, int], remainder: bytes = b"",
                 separator: bytes = b";", on_close: _Callable[[_Self], None] = lambda _: None) -> None:
        super().__init__(service, remainder, separator)
        self._socket: _socket = socket
        self._address: tuple[str, int] = address
        self._on_close: _Callable[[Connection], None] = on_close

    @_override
    def __str__(self) -> str:
        return self._address[0] + ":" + str(self._address[1])

    @_override
    def closed(self) -> bool:
        return self._socket.fileno() == -1

    def _require_open_socket(self, mandatory: bool = True) -> _socket:
        """
        Check if the socket is active and return it
        :param mandatory: True: an open socket is required; False: a closed socket is acceptable
        :return: the socket object
        """
        if mandatory and self.closed():
            raise IOError("An open socket is required")
        return self._socket

    @_override
    def receive(self, chunk_size: int = 512) -> bytes | None:
        """
        :param chunk_size: chunk buffer size
        :return: message in bytes or None
        """
        if self._remainder != b"":
            return self.use_remainder()
        try:
            msg = chunk = b""
            while self._separator not in chunk:
                msg += (chunk := self._require_open_socket().recv(chunk_size))
            return self.with_remainder(msg)
        except IOError:
            return

    @_override
    def send(self, msg: bytes) -> None:
        self._require_open_socket().send(msg + self._separator)
        if msg == b"disconnect":
            self.close()

    @_override
    def close(self) -> None:
        self._on_close(self)
        self._require_open_socket(False).close()


class Callback(CallbackChain):
    def on_initialize(self, service: Service) -> None: ...

    def on_fail(self, service: Service, error: Exception) -> None: ...

    def on_connect(self, service: Service, connection: ConnectionBase) -> None: ...

    def on_receive(self, service: Service, msg: bytes) -> None: ...

    def on_disconnect(self, service: Service, connection: ConnectionBase) -> None: ...


class Entity(Service, metaclass=_ABCMeta):
    def __init__(self, port: int, callback: Callback) -> None:
        """
        :param port: the port on which the service listens
        :param callback: the callback interface
        """
        super().__init__(port)
        self._callback: Callback = callback

    def set_callback(self, callback: Callback) -> None:
        callback.bind_chain(self._callback)
        self._callback = callback

    def _stage(self, connection: ConnectionBase) -> None:
        while _threads_life_flag.active:
            msg = connection.receive()
            if msg is None or msg == b"disconnect":
                self._callback.on_disconnect(self, connection)
                return connection.close()
            self._callback.on_receive(self, msg)

    @_override
    def _run(self, *args, **kwargs) -> None:
        try:
            return super()._run(*args, **kwargs)
        except Exception as e:
            self._callback.on_fail(self, e)
