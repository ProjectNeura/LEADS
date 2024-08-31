from typing import Any as _Any, override as _override

from leads.constant import ESCMode
from leads.context import Context
from leads.registry import require_context


class Plugin(object):
    def __init__(self, required_data: tuple[str, ...] = (), required_devices: tuple[str, ...] = ()) -> None:
        """
        :param required_data: required data entries
        :param required_devices: required device tags
        """
        super().__init__()
        self._required_data: tuple[str, ...] = required_data
        self._required_devices: tuple[str, ...] = required_devices
        self._enabled: bool = True

    def enabled(self, enabled: bool | None = None) -> bool | None:
        if enabled is None:
            return self._enabled
        self._enabled = enabled

    def required_data(self) -> tuple[str, ...]:
        return self._required_data

    def required_devices(self) -> tuple[str, ...]:
        return self._required_devices

    def on_load(self, context: Context) -> None: ...

    def pre_push(self, context: Context, kwargs: dict[str, _Any]) -> None:
        """
        Note that the new data at this point is not available yet.
        :param context: target context
        :param kwargs: {required data: its value}
        """
        ...

    def post_push(self, context: Context, kwargs: dict[str, _Any]) -> None:
        """
        :param context: target context
        :param kwargs: {required data: its value}
        """
        ...

    def pre_update(self, context: Context, kwargs: dict[str, _Any]) -> None:
        """
        :param context: target context
        :param kwargs: {required data: its value}
        """
        ...

    def post_update(self, context: Context, kwargs: dict[str, _Any]) -> None:
        """
        :param context: target context
        :param kwargs: {required data: its value}
        """
        ...


class ESCPlugin(Plugin):
    @_override
    def enabled(self, enabled: bool | None = None) -> bool | None:
        if enabled is None:
            return require_context().esc_mode() != ESCMode.OFF and super().enabled()
        super().enabled(enabled)

    @staticmethod
    def adjudicate(d: float, base: float, absolute: float, percentage: float) -> bool:
        return d > 0 and ((absolute and d > absolute) or (percentage and d > base * percentage))
