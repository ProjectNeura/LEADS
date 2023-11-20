from random import randint as _randint
from leads.controller.controller import T
from leads import Controller as _Controller, DefaultDataContainer as _DefaultDataContainer


class Random(_Controller):
    def collect_all(self) -> T:
        return _DefaultDataContainer(_randint(10, 40))
