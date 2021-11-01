from typing import Any, Dict, Iterator, Mapping, final


@final
class SettingsView(Mapping[str, Any]):
    __data: Mapping[str, Any]

    def __init__(self, mapping: Mapping[str, Any]) -> None:
        copied: Dict[str, Any] = {}
        for k, v in mapping.items():
            if isinstance(v, dict):
                copied[k] = SettingsView(v)
            else:
                copied[k] = v
        self.__data = copied

    def __getitem__(self, k: str) -> Any:
        return self.__data.__getitem__(k)

    def __iter__(self) -> Iterator[str]:
        return self.__data.__iter__()

    def __len__(self) -> int:
        return self.__data.__len__()
