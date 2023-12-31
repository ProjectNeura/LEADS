from time import time as _time

from leads import DataContainer as _DataContainer
from leads.comm import Server as _Server


class RuntimeData(object):
    start_time: int = int(_time())
    lap_time: list[int] = []
    frame_counter: int = 0
    comm: _Server | None = None

    def comm_notify(self, d: _DataContainer) -> None:
        if self.comm:
            self.comm.broadcast(d.encode())

    def comm_kill(self) -> None:
        if self.comm:
            self.comm.kill()
