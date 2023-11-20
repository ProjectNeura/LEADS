from time import time as _time


class RuntimeData(object):
    start_time: int = int(_time())
    frame_counter: int = 0
