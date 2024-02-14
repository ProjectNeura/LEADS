from leads import Controller as _Controller


class RaspberryPi4B(_Controller):
    def __init__(self, srw_mode: bool = True) -> None:
        super().__init__()
        self._srw_mode: bool = srw_mode

    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
