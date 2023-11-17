from .context import Context
from .event import EventListener


def initialize() -> Context:
    return Context(EventListener())
