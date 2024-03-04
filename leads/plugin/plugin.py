from typing import Any as _Any

from leads.constant import ECSMode
from leads.context import Context, ContextAssociated
from leads.types import RequiredData


class Plugin(ContextAssociated):
    def __init__(self, required_data: RequiredData) -> None:
        """
        :param required_data: required data or (required data in srw mode, required data in drw mode)
        """
        super().__init__()
        self._required_data: RequiredData = required_data
        self.state: dict[str, _Any] = {}
        self._enabled: bool = True

    def __getitem__(self, key: str) -> _Any:
        return self.state[key]

    def __setitem__(self, key: str, value: _Any) -> None:
        self.state[key] = value

    def enabled(self, enabled: bool | None = None) -> bool | None:
        if enabled is None:
            return self.require_context().ecs_mode() != ECSMode.OFF and self._enabled
        self._enabled = enabled

    def required_data(self) -> list[str]:
        return (self._required_data if isinstance(self._required_data, list) else
                self._required_data[0] if self.require_context().srw_mode() else self._required_data[1])

    def load(self) -> None:
        self.on_load(self.require_context())

    def on_load(self, context: Context) -> None:
        pass

    def update(self, kwargs: dict[str, _Any]) -> None:
        self.on_update(self.require_context(), kwargs)

    def on_update(self, context: Context, kwargs: dict[str, _Any]) -> None:
        pass
