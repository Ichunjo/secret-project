

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
        return self._data.__getitem__(k)

    def __setitem__(self, k: str, v: Any) -> None:
        self._data.__setitem__(k, v)
        log_update((self.__class__.__name__, k), v)

    def __delitem__(self, v: str) -> NoReturn:
        raise NotImplementedError

    def __iter__(self) -> Iterator[str]:
        return self._data.__iter__()

    def __len__(self) -> int:
        return self._data.__len__()

    def __str__(self) -> str:
        return self._data.__str__()

    __repr__ = __str__
