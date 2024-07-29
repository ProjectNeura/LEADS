from json import load as _load
from os import listdir as _listdir
from os.path import abspath as _abspath

from leads_sus.gui import *
from leads_sus.user import *

_USERS_PATH: str = f"{_abspath(__file__)[:-11]}users"
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
