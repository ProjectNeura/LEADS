from random import randint as _randint

from leads import Controller as _Controller, SRWDataContainer as _SRWDataContainer, \
    DRWDataContainer as _DRWDataContainer


class SRWRandom(_Controller):
    def __init__(self, tag: str, minimum: int = 30, maximum: int = 40):
        super().__init__(tag)
        self.minimum: int = minimum
        self.maximum: int = maximum

    def collect_all(self) -> _SRWDataContainer:
        return _SRWDataContainer(ws := _randint(self.minimum, self.maximum), ws)


class DRWRandom(_Controller):
    def __init__(self, tag: str, minimum: int = 30, maximum: int = 40):
        super().__init__(tag)
        self.minimum: int = minimum
        self.maximum: int = maximum

    def collect_all(self) -> _DRWDataContainer:
        return _DRWDataContainer(ws := _randint(self.minimum, self.maximum), ws, ws)
