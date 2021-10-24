

# from _typeshed import SupportsKeysAndGetItem
from abc import ABC
from typing import Any, Dict, Iterator, MutableMapping, NoReturn

from ..logger import log_update


class LoggedSettings(MutableMapping[str, Any], ABC):
    _data: Dict[str, Any]

    def __init__(self, **d: Any) -> None:
        self._data = d
        super().__init__()

    def __getitem__(self, k: str) -> Any:
        return self._data[k]

    def __setitem__(self, k: str, v: Any) -> None:
        self._data[k] = v
        log_update((self.__class__.__name__, k), v)

    def __delitem__(self, v: str) -> NoReturn:
        raise NotImplementedError

    def __iter__(self) -> Iterator[str]:
        yield from self._data

    def __len__(self) -> int:
        return len(self._data)

    def __str__(self) -> str:
        return dict.__str__(self._data)

    __repr__ = __str__
