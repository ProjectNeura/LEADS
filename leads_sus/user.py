from json import dump as _dump, load as _load
from os import listdir as _listdir
from os.path import abspath as _abspath
from typing import TypeVar as _TypeVar

from leads.types import SupportedConfig as _SupportedConfig

T = _TypeVar("T", bound=_SupportedConfig)

_USERS_PATH: str = f"{_abspath(__file__)[:-7]}users"


class User(object):
    def __init__(self, name: str, **kwargs) -> None:
        self._name: str = name
        self._data: dict[str, _SupportedConfig] = {"name": name, **kwargs}

    def name(self) -> str:
        return self._name

    def set(self, key: str, value: _SupportedConfig) -> None:
        if key == "name":
            if not isinstance(value, str):
                raise TypeError("Name must be a string")
            self._name = value
        self._data[key] = value

    def require(self, key: str, required_type: type[T], default: T) -> T:
        if (r := self._data[key]) is None:
            return default
        if not isinstance(r, required_type):
            raise TypeError(f"Required type {required_type} but got {type(r)} instead")
        return r

    def save(self) -> None:
        with open(f"{_USERS_PATH}/{self._name.lower()}.json", "w") as f:
            _dump(self._data, f)


_users: dict[str, User] = {}
for _source in _listdir(_USERS_PATH):
    with open(f"{_USERS_PATH}/{_source}") as _f:
        _u = User(**_load(_f))
        _users[_u.name()] = _u


def list_user_names() -> tuple[str, ...]:
    return tuple(_users.keys())


def list_users() -> list[User]:
    return list(_users.values())


def get_user(name: str) -> User:
    return _users[name]
