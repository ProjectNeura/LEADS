from json import dumps as _dumps
from time import time as _time
from typing import Any as _Any

from leads import DataContainer as _DataContainer
from leads.comm import Server as _Server


class RuntimeData(object):
    start_time: int = int(_time())
    lap_time: list[int] = []
    comm: _Server | None = None

    def comm_notify(self, d: _DataContainer | dict[str, _Any]) -> None:
        if self.comm:
            self.comm.broadcast(d.encode() if isinstance(d, _DataContainer) else _dumps(d).encode())
