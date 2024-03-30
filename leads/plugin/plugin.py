from typing import Any as _Any

from leads.constant import ESCMode
from leads.context import Context
from leads.registry import require_context
from leads.types import RequiredData as _RequiredData


class Plugin(object):
    def __init__(self, required_data: _RequiredData) -> None:
        """
        :param required_data: required data or (required data in srw mode, required data in drw mode)
        """
        super().__init__()
        self._required_data: _RequiredData = required_data
        self.state: dict[str, _Any] = {}
        self._enabled: bool = True

    def __getitem__(self, key: str) -> _Any:
        return self.state[key]

    def __setitem__(self, key: str, value: _Any) -> None:
        self.state[key] = value

    def enabled(self, enabled: bool | None = None) -> bool | None:
        if enabled is None:
            return require_context().esc_mode() != ESCMode.OFF and self._enabled
        self._enabled = enabled

    def required_data(self) -> list[str]:
        return (self._required_data if isinstance(self._required_data, list) else
                self._required_data[0] if require_context().srw_mode() else self._required_data[1])

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
