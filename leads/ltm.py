from json import loads as _loads, dumps as _dumps
from os import chmod as _chmod, access as _access, R_OK as _R_OK, W_OK as _W_OK
from os.path import abspath as _abspath, exists as _exists

from leads.logger import L
from leads.types import SupportedConfigValue as _SupportedConfigValue

_PATH: str = f"{_abspath(__file__)[:-6]}_ltm/core"

_ltm: dict[str, _SupportedConfigValue] = {}


def _acquire_permission() -> bool:
    if _access(_PATH, _R_OK) and _access(_PATH, _W_OK):
        return True
    L.debug(f"Attempting to acquire permission for {_PATH}")
    try:
        _chmod(_PATH, 0o666)
        return True
    except Exception as e:
        L.debug(f"Failed to acquire permission: {repr(e)}")
        L.debug(f"Try executing `sudo chmod 666 {_PATH}` manually or run LEADS as the root user")
        return False


def _load_ltm() -> None:
    if not _permission_ok:
        return
    global _ltm
    try:
        if not _exists(_PATH):
            with open(_PATH, "w") as f:
                f.write("{}")
            return
        with open(_PATH) as f:
            ltm_content = f.read()
            if not (ltm_content.startswith("{") and ltm_content.endswith("}")):
                ltm_content = "{}"
            _ltm = _loads(ltm_content)
    except Exception as e:
        L.warn(f"Attempted but failed to load LTM: {repr(e)}")


def _sync_ltm() -> None:
    if not _permission_ok:
        return
    try:
        with open(_PATH, "w") as f:
            f.write(_dumps(_ltm))
    except Exception as e:
        L.warn(f"Attempted but failed to sync LTM: {repr(e)}")


def ltm_get(key: str) -> _SupportedConfigValue:
    return _ltm[key]


def ltm_set(key: str, value: _SupportedConfigValue) -> None:
    _ltm[key] = value
    _sync_ltm()


_permission_ok: bool = _acquire_permission()
L.debug(f"LTM permission {"OK" if _permission_ok else "NOT OK"}: {_PATH}")
_load_ltm()
