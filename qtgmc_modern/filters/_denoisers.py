"""
Denoiser interface
"""


__all__ = [
    'Denoiser',
    'DFTTest', 'NeoDFTTest',
    'KNLMeansCL',
    'FFT3D', 'NeoFFT3D',
    'DeviceTypeCL', 'KNLMeansCLChannel', 'knl_means_cl'
]

from abc import ABC
from enum import Enum
from typing import Any

import vapoursynth as vs

from ..better_vsutil import is_444
from ._abstract import VSFilter

core = vs.core


class Denoiser(VSFilter, ABC):
    def __call__(self, clip: vs.VideoNode, **kwargs: Any) -> vs.VideoNode:
        return super().__vscall__(clip, **kwargs)


class DFTTest(Denoiser):
    func = lambda: core.dfttest.DFTTest


class NeoDFTTest(Denoiser):
    func = lambda: core.neo_dfttest.DFTTest


class KNLMeansCL(Denoiser):
    func = lambda: knl_means_cl


class FFT3D(Denoiser):
    func = lambda: core.fft3dfilter.FFT3DFilter


class NeoFFT3D(Denoiser):
    func = lambda: core.neo_fft3d.FFT3D


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
