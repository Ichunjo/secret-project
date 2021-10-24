from __future__ import annotations

from functools import partial, wraps
from typing import (Any, Callable, Dict, Optional, Protocol, TypeVar, Union,
                    cast, overload)

import vapoursynth as vs
from typing_extensions import Concatenate, ParamSpec

_T_co = TypeVar('_T_co', covariant=True)
_P = ParamSpec('_P')


class HasParam(Protocol):
    params: Dict[str, Any]


# class ObjectsYUV(Sequence[_T_co]):
#     _objs: Tuple[_T_co, ...]

#     def __init__(self, value: _T_co | Sequence[_T_co]) -> None:
#         if isinstance(value, Sequence):
#             value = list(value)
#             self._objs = tuple(value + [value[-1]] * (3 - len(value)))
#         else:
#             self._objs = (value, ) * 3

#     @overload
#     def __getitem__(self, x: int) -> _T_co:
#         ...

#     @overload
#     def __getitem__(self, x: slice) -> Tuple[_T_co, ...]:
#         ...

#     def __getitem__(self, x: int | slice) -> _T_co | Tuple[_T_co, ...]:
#         return self._objs[x]

#     @property
#     def Y(self) -> _T_co:
#         return self._objs[0]

#     @property
#     def U(self) -> _T_co:
#         return self._objs[1]

#     @property
#     def V(self) -> _T_co:
#         return self._objs[2]


def merge_chroma(y: vs.VideoNode, uv: vs.VideoNode, /) -> vs.VideoNode:
    return vs.core.std.ShufflePlanes([y, uv], [0, 1, 2], vs.YUV)


CallMethod = Callable[Concatenate[HasParam, vs.VideoNode, int, _P], vs.VideoNode]


@overload
def inject_param(*, name: str = '') -> Callable[[CallMethod], CallMethod]:
    ...


@overload
def inject_param(method: Optional[CallMethod] = None, /) -> CallMethod:
    ...


def inject_param(
    method: Optional[CallMethod] = None, name: str = ''
) -> Union[Callable[[CallMethod], CallMethod], CallMethod]:

    if method is None:
        return cast(
            Callable[[CallMethod], CallMethod],
            partial(inject_param, name=name)
        )

    @wraps(method)
    def wrapper(self: HasParam, clip: vs.VideoNode, field: int, *args: _P.args, **kwargs: _P.kwargs) -> vs.VideoNode:
        try:
            scliper = self.params.pop('external_deint_clip')
        except KeyError:
            pass
        else:
            self.params.update([(name, scliper(clip, field))])
        return method(self, clip, field, *args, **kwargs)

    return wrapper


Nb = TypeVar('Nb', bound=Union[float, int])  # Number


def clamp_value(val: Nb, min_val: Nb, max_val: Nb) -> Nb:
    """
    Clamp value val between min_val and max_val

    :param val:         Value to clamp
    :param min_val:     Minimum value
    :param max_val:     Maximum value
    :return:            Clamped value
    """
    return min_val if val < min_val else max_val if val > max_val else val
