from json import loads as _loads, dumps as _dumps
from os.path import abspath as _abspath

from leads.types import SupportedConfigValue as _SupportedConfigValue

_ltm: dict[str, _SupportedConfigValue] = {}


def _load_ltm() -> None:
    global _ltm
    with open(f"{_abspath(__file__)[:-6]}_ltm/core", "r") as f:
        ltm_content = f.read()
        if not (ltm_content.startswith("{") and ltm_content.endswith("}")):
            ltm_content = "{}"
        _ltm = _loads(ltm_content)


def _sync_ltm() -> None:
    with open(f"{_abspath(__file__)[:-6]}_ltm/core", "w") as f:
        f.write(_dumps(_ltm))


def ltm_get(key: str) -> _SupportedConfigValue:
    return _ltm[key]


def ltm_set(key: str, value: _SupportedConfigValue) -> None:
    _ltm[key] = value
    _sync_ltm()


_load_ltm()
