from typing import override as _override

from can import Bus as _Bus, Notifier as _Notifier, Listener as _Listener, Message as _Message

from leads import Controller as _Controller


class CANBus(_Controller, _Listener):
    def __init__(self) -> None:
        _Controller.__init__(self)
        _Listener.__init__(self)
        self._bus: _Bus | None = None
        self._notifier: _Notifier | None = None

    @_override
    def on_message_received(self, msg: _Message) -> None:
        for device in self.devices():
            device.update(msg)

    @_override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        self._bus = _Bus()
        self._notifier = _Notifier(self._bus, (self,))

    @_override
    def write(self, payload: _Message) -> None:
        self._bus.send(payload)

    @_override
    def close(self) -> None:
        self._bus.close()
