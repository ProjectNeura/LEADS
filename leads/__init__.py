from atexit import register as _register

from leads.config import *
from leads.context import *
from leads.data import *
from leads.dt import *
from leads.event import *
from leads.leads import *
from leads.logger import Level, L
from leads.os import _thread_flags
from leads.plugin import *
from leads.registry import *
from leads.sft import SFT, mark_system, read_marked_system


@_register
def _request_threads_stop() -> None:
    _thread_flags.active = False
