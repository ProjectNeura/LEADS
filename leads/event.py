from typing import Any as _Any

from leads.context import Context
from leads.data import DataContainer


class Event(object):
    def __init__(self, t: str, context: Context) -> None:
        self.context: Context = context
        self.t: str = t

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
    def __init__(self, context: Context, system: str, cause: str) -> None:
        super().__init__("SUSPENSION", context, system)
        self.cause: str = cause


class EventListener(object):
    def on_push(self, event: DataPushedEvent) -> None:
        pass

    def post_push(self, event: DataPushedEvent) -> None:
        pass

    def on_update(self, event: UpdateEvent) -> None:
        pass

    def post_update(self, event: UpdateEvent) -> None:
        pass

    def on_intervene(self, event: InterventionEvent) -> None:
        pass

    def post_intervene(self, event: InterventionExitEvent) -> None:
        pass

    def on_suspend(self, event: SuspensionEvent) -> None:
        pass

    def post_suspend(self, event: SuspensionEvent) -> None:
        pass
