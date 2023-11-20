class Device(object):
    def __init__(self, tag: str, *pins: int | str):
        self._tag: str = tag
        self._pins: tuple[int | str] = pins

    def tag(self) -> str:
        return self._tag
