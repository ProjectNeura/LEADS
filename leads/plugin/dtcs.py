from leads.context import Context
from leads.plugin.plugin import Plugin


class DTCS(Plugin):
    def __init__(self):
        super(DTCS, self).__init__()

    def on_update(self, context: Context) -> None:
        pass
