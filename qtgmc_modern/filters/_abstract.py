

from abc import ABC
from typing import Any, Callable, ClassVar, Dict, Protocol, Type, TypeVar, cast

import vapoursynth as vs

_VSFilter = TypeVar('_VSFilter', bound='VSFilter')


class Func(Protocol[vs.VideoNode]):
    def __call__(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
        ...


class HasFunc(Protocol[Callable[[], Func]]):
    def __func__(self) -> Func:
        ...


class VSFilter(ABC):
    params: Dict[str, Any]
    func: ClassVar[Callable[[], Callable[..., vs.VideoNode]]]

    def __init__(self, **kwargs: Any) -> None:
        self.params = kwargs
        super().__init__()

    def __str__(self) -> str:
        params = ', '.join(f'{k}={v}' for k, v in self.params.items())
        return f'{self.__class__.__name__}({params})'

    __repr__ = __str__

    def __vscall__(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
        return self.get_func(clip, *args, **self.params | kwargs)

    @property
    def get_func(self) -> Func:
        return cast(HasFunc, self.func).__func__()

    def swap(self, new: Type[_VSFilter]) -> _VSFilter:
        return new(**self.params)
