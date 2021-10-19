
__all__ = [
    'Zimg',

    'Point',

    'Bilinear',

    'Bicubic',
    'BSpline', 'Hermite', 'Mitchell', 'Catrom', 'BicubicSharp',
    'RobidouxSoft', 'Robidoux', 'RobidouxSharp',

    'Lanczos',

    'Spline16', 'Spline36', 'Spline64'
]

from abc import ABC
from math import sqrt
from typing import Any, Callable, ClassVar, NamedTuple

import vapoursynth as vs
from typing_extensions import Concatenate, ParamSpec

from ._abstract import AbstractBicubic, AbstractWindowed, Kernel, ScaleIsCall

core = vs.core

_P = ParamSpec('_P')
_Scaler = Callable[Concatenate[vs.VideoNode, _P], vs.VideoNode]
_Descaler = Callable[Concatenate[vs.VideoNode, int, int, _P], vs.VideoNode]


class _Resizers(NamedTuple):
    scaler: _Scaler
    descaler: _Descaler


class Zimg(ScaleIsCall, Kernel, ABC):
    resizer: ClassVar[_Resizers]

    def __call__(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
        return self.resizer.scaler(clip, *args, **self.params | kwargs)

    def descale(self, clip: vs.VideoNode, width: int, height: int, **kwargs: Any) -> vs.VideoNode:
        return self.resizer.descaler(clip, width, height, **self.params | kwargs)


class Point(Zimg):
    resizer = _Resizers(core.resize.Point, core.resize.Point)


class Bilinear(Zimg):
    resizer = _Resizers(core.resize.Bilinear, core.descale.Debilinear)


class Bicubic(Zimg, AbstractBicubic):
    resizer = _Resizers(core.resize.Bicubic, core.descale.Debicubic)

    def __call__(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
        return super().__call__(clip, *args, **dict(filter_param_a=self.b, filter_param_b=self.c) | self.params | kwargs)

    def descale(self, clip: vs.VideoNode, width: int, height: int, **kwargs: Any) -> vs.VideoNode:
        return super().descale(clip, width, height, b=self.b, c=self.c, **self.params | kwargs)


class BSpline(Bicubic):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(b=1, c=0, **kwargs)


class Hermite(Bicubic):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(b=0, c=0, **kwargs)


class Mitchell(Bicubic):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(b=1/3, c=1/3, **kwargs)


class Catrom(Bicubic):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(b=0, c=1/2, **kwargs)


class BicubicSharp(Bicubic):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(b=0, c=1, **kwargs)


class RobidouxSoft(Bicubic):
    def __init__(self, **kwargs: Any) -> None:
        b = (9 - 3 * sqrt(2)) / 7
        c = (1 - b) / 2
        super().__init__(b=b, c=c, **kwargs)


class Robidoux(Bicubic):
    def __init__(self, **kwargs: Any) -> None:
        b = 12 / (19 + 9 * sqrt(2))
        c = 113 / (58 + 216 * sqrt(2))
        super().__init__(b=b, c=c, **kwargs)


class RobidouxSharp(Bicubic):
    def __init__(self, **kwargs: Any) -> None:
        b = 6 / (13 + 7 * sqrt(2))
        c = 7 / (2 + 12 * sqrt(2))
        super().__init__(b=b, c=c, **kwargs)


class Lanczos(Zimg, AbstractWindowed):
    resizer = _Resizers(core.resize.Lanczos, core.descale.Delanczos)

    def __call__(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
        return super().__call__(clip, *args, **dict(filter_param_a=self.taps) | self.params | kwargs)

    def descale(self, clip: vs.VideoNode, width: int, height: int, **kwargs: Any) -> vs.VideoNode:
        return super().descale(clip, width, height, taps=self.taps, **self.params | kwargs)


class Spline16(Zimg):
    resizer = _Resizers(core.resize.Spline16, core.descale.Despline16)


class Spline36(Zimg):
    resizer = _Resizers(core.resize.Spline36, core.descale.Despline36)


class Spline64(Zimg):
    resizer = _Resizers(core.resize.Spline64, core.descale.Despline64)


# class Spline(ScaleIsCall, AbstractSpline):
#     def __call__(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
#         spliners: Dict[int, Callable[..., vs.VideoNode]] = {
#             4: core.resize.Spline16,
#             6: core.resize.Spline36,
#             8: core.resize.Spline64
#         }
#         try:
#             spline = spliners[self.sample_points]
#         except KeyError as key_err:
#             raise ValueError() from key_err
#         return spline(clip, *args, **self.params | kwargs)

#     def descale(self, clip: vs.VideoNode, width: int, height: int, **kwargs: Any) -> vs.VideoNode:
#         despliners: Dict[int, Callable[..., vs.VideoNode]] = {
#             4: core.descale.Despline16,
#             6: core.descale.Despline36,
#             8: core.descale.Despline64
#         }
#         try:
#             despline = despliners[self.sample_points]
#         except KeyError as key_err:
#             raise ValueError() from key_err
#         return despline(clip, width, height, **self.params | kwargs)


# class Spline16(Spline):
#     def __init__(self, **kwargs: Any) -> None:
#         super().__init__(sample_points=4, **kwargs)


# class Spline36(Spline):
#     def __init__(self, **kwargs: Any) -> None:
#         super().__init__(sample_points=6, **kwargs)


# class Spline64(Spline):
#     def __init__(self, **kwargs: Any) -> None:
#         super().__init__(sample_points=8, **kwargs)
