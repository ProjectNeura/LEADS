from time import time as _time

from leads import DataContainer as _DataContainer
from leads.comm import Client as _Client


class RuntimeData(object):
    start_time: int = int(_time())
    lap_time: list[int] = []
    frame_counter: int = 0
    comm: _Client | None = None

    def comm_notify(self, d: _DataContainer):
        if self.comm:
            self.comm.send(d.encode())

    def comm_kill(self):
        if self.comm:
            self.comm.kill()
