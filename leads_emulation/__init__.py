from random import randint as _randint

from leads import Controller as _Controller, SRWDataContainer as _SRWDataContainer, \
    DRWDataContainer as _DRWDataContainer


class SRWRandom(_Controller):
    def collect_all(self) -> _SRWDataContainer:
        return _SRWDataContainer(ws := _randint(30, 35), ws)


class DRWRandom(_Controller):
    def collect_all(self) -> _DRWDataContainer:
        return _DRWDataContainer(ws := _randint(30, 35), ws, ws)
