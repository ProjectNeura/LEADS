from typing import Any as _Any

from leads.context import Context

type RequiredData = list[str] | tuple[list[str], list[str]]


class Plugin(object):
    def __init__(self, required_data: RequiredData) -> None:
        """
        :param required_data: required data or (required data in srw mode, required data in drw mode)
        """
        self._required_data: RequiredData = required_data
        self.state: dict[str, _Any] = {}
        self.enabled: bool = True
        self._context: Context | None = None

    def __getitem__(self, key: str) -> _Any:
        return self.state[key]

    def __setitem__(self, key: str, value: _Any) -> None:
        self.state[key] = value

    def bind_context(self, context: Context) -> None:
        self._context = context

    def _require_context(self) -> Context:
        if self._context:
            return self._context
        raise RuntimeError("No context bound")

    def required_data(self) -> list[str]:
        return (self._required_data if isinstance(self._required_data, list)
                else self._required_data[0] if self._require_context().srw_mode()
        else self._required_data[1])

    def load(self) -> None:
        self.on_load(self._require_context())

    def on_load(self, context: Context) -> None:
        pass

    def update(self, kwargs: dict[str, _Any]) -> None:
        self.on_update(self._require_context(), kwargs)

    def on_update(self, context: Context, kwargs: dict[str, _Any]) -> None:
        pass
