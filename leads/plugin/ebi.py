from leads.plugin.plugin import ESCPlugin


class EBI(ESCPlugin):
    def __init__(self) -> None:
        super().__init__(("front_wheel_speed",))
