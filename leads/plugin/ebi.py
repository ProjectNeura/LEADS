from leads.plugin.plugin import Plugin


class EBI(Plugin):
    def __init__(self) -> None:
        super().__init__(["front_wheel_speed"])
