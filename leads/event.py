from .context import Context


class Event(object):
    def __init__(self, t: str, context: Context):
        self.context: Context = context
        self.t: str = t

    def __str__(self) -> str:
        return f"[{self.t}] {self.context.data()}"


class DataPushedEvent(Event):
    def __init__(self, context: Context):
        super().__init__("DATA PUSHED", context)


class UpdateEvent(Event):
    def __init__(self, context: Context):
        super().__init__("UPDATE", context)


class InterventionEvent(Event):
    def __init__(self, context: Context):
        super().__init__("INTERVENTION", context)


class EventListener(object):
    def on_push(self, event: DataPushedEvent):
        pass

    def on_update(self, event: UpdateEvent):
        pass

    def on_intervene(self, event: InterventionEvent):
        pass
