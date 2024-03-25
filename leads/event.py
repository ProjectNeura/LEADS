from typing import Any as _Any, override as _override, Self as _Self

from leads.context import Context
from leads.data import DataContainer
from leads.os import currentframe


class Event(object):
    def __init__(self, t: str, context: Context) -> None:
        self.context: Context = context
        self.t: str = t

    @_override
    def __str__(self) -> str:
        return f"[{self.t}] {self.context.data()}"


class DataPushedEvent(Event):
    def __init__(self, context: Context, data: DataContainer) -> None:
        super().__init__("DATA PUSHED", context)
        self.data: DataContainer = data


class UpdateEvent(Event):
    def __init__(self, context: Context) -> None:
        super().__init__("UPDATE", context)


class SystemEvent(Event):
    def __init__(self, t: str, context: Context, system: str) -> None:
        super().__init__(t, context)
        self.system: str = system


class InterventionEvent(SystemEvent):
    def __init__(self, context: Context, system: str, *data: _Any) -> None:
        super().__init__("INTERVENTION", context, system)
        self.data: tuple[_Any, ...] = data


class InterventionExitEvent(InterventionEvent):
    pass


class SuspensionEvent(SystemEvent):
    def __init__(self, context: Context, system: str, cause: str, fatal: bool = False) -> None:
        super().__init__("SUSPENSION", context, system)
        self.cause: str = cause
        self.fatal: bool = fatal


class EventListener(object):
    def __init__(self, chain: _Self | None = None) -> None:
        self._chain: EventListener | None = chain

    def super(self, e: Event) -> None:
        """
        Call the superior method if there is one.
        This must be called directly in the corresponding successor method.
        """
        if self._chain:
            getattr(self._chain, currentframe().f_back.f_code.co_name)(e)

    def on_push(self, event: DataPushedEvent) -> None: ...

    def post_push(self, event: DataPushedEvent) -> None: ...

    def on_update(self, event: UpdateEvent) -> None: ...

    def post_update(self, event: UpdateEvent) -> None: ...

    def on_intervene(self, event: InterventionEvent) -> None: ...

    def post_intervene(self, event: InterventionExitEvent) -> None: ...

    def on_suspend(self, event: SuspensionEvent) -> None: ...

    def post_suspend(self, event: SuspensionEvent) -> None: ...
