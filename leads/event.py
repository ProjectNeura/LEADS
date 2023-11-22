from typing import Any as _Any

from .context import Context
from .data import DataContainer


class Event(object):
    def __init__(self, t: str, context: Context):
        self.context: Context = context
        self.t: str = t

    def __str__(self) -> str:
        return f"[{self.t}] {self.context.data()}"


class DataPushedEvent(Event):
    def __init__(self, context: Context, data: DataContainer):
        super().__init__("DATA PUSHED", context)
        self.data: DataContainer = data


class UpdateEvent(Event):
    def __init__(self, context: Context):
        super().__init__("UPDATE", context)


class SystemEvent(Event):
    def __init__(self, t: str, context: Context, system: str):
        super().__init__(t, context)
        self.system: str = system


class InterventionEvent(SystemEvent):
    def __init__(self, context: Context, system: str, *data: _Any):
        super().__init__("INTERVENTION", context, system)
        self.data: tuple[_Any] = data


class SuspensionEvent(SystemEvent):
    def __init__(self, context: Context, system: str, cause: str):
        super().__init__("SUSPENSION", context, system)
        self.cause: str = cause


class EventListener(object):
    def on_push(self, event: DataPushedEvent):
        pass

    def post_push(self, event: DataPushedEvent):
        pass

    def on_update(self, event: UpdateEvent):
        pass

    def post_update(self, event: UpdateEvent):
        pass

    def on_intervene(self, event: InterventionEvent):
        pass

    def post_intervene(self, event: InterventionEvent):
        pass

    def on_suspend(self, event: SuspensionEvent):
        pass

    def post_suspend(self, event: SuspensionEvent):
        pass
