from random import randint as _randint
from leads import Controller as _Controller, SRWDataContainer as _SRWDataContainer, DRWDataContainer as _DRWDataContainer


class SRWRandom(_Controller):
    def collect_all(self) -> _SRWDataContainer:
        ws = _randint(10, 40)
        return _SRWDataContainer(ws, ws, ws)


class DRWRandom(_Controller):
    def collect_all(self) -> _DRWDataContainer:
        ws = _randint(10, 40)
        return _DRWDataContainer(ws, ws, ws, ws)
