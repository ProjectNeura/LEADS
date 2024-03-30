from typing import Self as _Self

from leads.os import _currentframe


class CallbackChain(object):
    def __init__(self, chain: _Self | None = None) -> None:
        self._chain: CallbackChain | None = chain

    def bind_chain(self, chain: _Self | None) -> None:
        self._chain = chain

    def super(self, *args, **kwargs) -> None:
        """
        Call the superior method if there is one.
        This must be called directly in the corresponding successor method.
        """
        cf = _currentframe().f_back
        while (cn := cf.f_code.co_name) == "super":
            cf = cf.f_back
        if self._chain:
            getattr(self._chain, cn)(*args, **kwargs)
