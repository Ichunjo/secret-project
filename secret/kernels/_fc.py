
__all__ = [
    'PointFC',

    'Box', 'Rect',

    'BilinearFC',

    'BicubicFC',

    'LanczosFC', 'Blackman', 'BlackmanMinLobe', 'Sinc',

    'SplineFC',
    'Spline16FC', 'Spline36FC', 'Spline64FC',

    'Gauss'
]

from abc import ABC
from enum import Enum
from typing import Any, ClassVar

import vapoursynth as vs

from ._abstract import (AbstractBicubic, AbstractSpline, AbstractWindowed,
                        Kernel, ScaleIsCall)

core = vs.core


class _FmtConvKernel(str, Enum):
    POINT = 'point'
    BOX = 'box'
    RECT = BOX
    BILINEAR = 'bilinear'
    BICUBIC = 'bicubic'
    LANCZOS = 'lanczos'
    BLACKMAN = 'blackman'
    BLACKMANMINLOBE = 'blackmanminlobe'
    SINC = 'sinc'
    SPLINE = 'spline'
    SPLINE16 = 'spline16'
    SPLINE36 = 'spline36'
    SPLINE64 = 'spline64'
    GAUSS = 'gauss'


class _FmtConv(ScaleIsCall, Kernel, ABC):
    kernel: ClassVar[_FmtConvKernel]

    def __call__(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
        return clip.fmtc.resample(*args, kernel=self.kernel, **self.params | kwargs)

    def descale(self, clip: vs.VideoNode, width: int, height: int, **kwargs: Any) -> vs.VideoNode:
        return self.__call__(clip, width, height, invks=True, **kwargs)



class PointFC(_FmtConv):
    kernel = _FmtConvKernel.POINT


class Box(_FmtConv):
    kernel = _FmtConvKernel.BOX


class Rect(Box):
    ...


class BilinearFC(_FmtConv):
    kernel = _FmtConvKernel.BILINEAR


class BicubicFC(_FmtConv, AbstractBicubic):
    kernel = _FmtConvKernel.BICUBIC

    def __call__(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
        return super().__call__(clip, *args, a1=self.b, a2=self.c, **self.params | kwargs)


class _WindowedFC(_FmtConv, AbstractWindowed, ABC):
    def __call__(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
        return super().__call__(clip, *args, taps=self.taps, **kwargs)


class LanczosFC(_WindowedFC):
    kernel = _FmtConvKernel.LANCZOS


class Blackman(_WindowedFC):
    kernel = _FmtConvKernel.BLACKMAN


class BlackmanMinLobe(_WindowedFC):
    kernel = _FmtConvKernel.BLACKMANMINLOBE


class Sinc(_WindowedFC):
    kernel = _FmtConvKernel.SINC


class SplineFC(_FmtConv, AbstractSpline, ABC):
    kernel = _FmtConvKernel.SPLINE

    def __call__(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
        return super().__call__(clip, *args, taps=self.sample_points, **kwargs)


class Spline16FC(_FmtConv):
    kernel = _FmtConvKernel.SPLINE16


class Spline36FC(_FmtConv):
    kernel = _FmtConvKernel.SPLINE36


class Spline64FC(_FmtConv):
    kernel = _FmtConvKernel.SPLINE64


class Gauss(_FmtConv):
    kernel = _FmtConvKernel.GAUSS
    p: int

    def __init__(self, p: int = 30, **kwargs: Any) -> None:
        self.p = p
        super().__init__(**kwargs)

    def __call__(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
        return super().__call__(clip, *args, a1=self.p, **kwargs)
