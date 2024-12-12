from typing import override as _override

from gpiozero import Button as _Button

from leads import Device as _Device, CallbackChain as _CallbackChain


class ButtonCallback(_CallbackChain):
    def on_pressed(self) -> None: ...

    def on_released(self) -> None: ...


class Button(_Device):
    """
    Listen to a button.
    Supports:
    - Any binary button
    """

    def __init__(self, pin: int, callback: ButtonCallback = ButtonCallback()) -> None:
        super().__init__(pin)
        self._button: _Button = _Button(pin)
        self._callback: ButtonCallback = callback

    def _when_activated(self) -> None:
        self._callback.on_pressed()

    def _when_deactivated(self) -> None:
        self._callback.on_released()

    @_override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        self._button.when_activated = self._when_activated
        self._button.when_deactivated = self._when_deactivated

    @_override
    def read(self) -> bool:
        return self._button.is_active

    @_override
    def write(self, callback: ButtonCallback) -> None:
        callback.bind_chain(self._callback)
        self._callback = callback
