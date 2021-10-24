
from abc import ABC
from enum import Enum
from typing import Any, Callable, ClassVar, Dict, Type, TypeVar

import vapoursynth as vs
from typing_extensions import Concatenate, ParamSpec

from .better_vsutil import is_444

core = vs.core


_P = ParamSpec('_P')
_DenFuncType = Callable[Concatenate[vs.VideoNode, _P], vs.VideoNode]
_Denoiser = TypeVar('_Denoiser', bound='Denoiser')


class Denoiser(ABC):
    params: Dict[str, Any]
    denoiser: ClassVar[Callable[[], _DenFuncType]]

    def __init__(self, **kwargs: Any) -> None:
        self.params = kwargs
        super().__init__()

    def __call__(self, clip: vs.VideoNode, **kwargs: Any) -> vs.VideoNode:
        return self.denoiser.__func__()(clip, **self.params | kwargs)

    def __str__(self) -> str:
        params = ', '.join(f'{k}={v}' for k, v in self.params.items())
        return f'{self.__class__.__name__}({params})'

    __repr__ = __str__

    def swap(self, denoiser: Type[_Denoiser]) -> _Denoiser:
        return denoiser(**self.params)


class DFTTest(Denoiser):
    denoiser = lambda: core.dfttest.DFTTest


class NeoDFTTest(Denoiser):
    denoiser = lambda: core.neo_dfttest.DFTTest


class KNLMeansCL(Denoiser):
    denoiser = lambda: knl_means_cl


class FFT3D(Denoiser):
    denoiser = lambda: core.fft3dfilter.FFT3DFilter


class NeoFFT3D(Denoiser):
    denoiser = lambda: core.neo_fft3d.FFT3D


class DeviceTypeCL(str, Enum):
    ACCEL = 'accelerator'
    ACCELERATOR = ACCEL
    CPU = 'cpu'
    GPU = 'gpu'
    AUTO = 'auto'


class KNLMeansCLChannel(str, Enum):
    YUV = 'YUV'
    Y = 'Y'
    UV = 'UV'


def knl_means_cl(
    clip: vs.VideoNode, strength: float = 1.2,
    tmprange: int = 1, radsearch: int = 2, radsim: int = 4,
    channels: KNLMeansCLChannel = KNLMeansCLChannel.YUV,
    **kwargs: Any
) -> vs.VideoNode:

    knl_args = dict(d=tmprange, a=radsearch, s=radsim, h=strength) | kwargs
    if channels == KNLMeansCLChannel.YUV:
        if is_444(clip):
            return clip.knlm.KNLMeansCL(**knl_args, channels=channels)
        return clip.knlm.KNLMeansCL(
            **knl_args, channels=KNLMeansCLChannel.Y
        ).knlm.KNLMeansCL(
            **knl_args, channels=KNLMeansCLChannel.UV
        )

    return clip.knlm.KNLMeansCL(**knl_args, channels=channels)
