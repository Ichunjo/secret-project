
__all__ = [
    'Deinterlacer',
    'NNEDI3', 'NNEDI3CL', 'ZNEDI3', 'ZNEDI3',
    'EEDI2',
    'EEDI3', 'EEDI3m', 'EEDI3mCL',
    'SangNom2',
    'BWDiF',
    'Bob',

    'NoiseDeint',
    'NoiseDWeave', 'NoiseBob', 'NoiseGenerate'
]

from abc import ABC, abstractmethod
from typing import Any, TypeVar, cast

import vapoursynth as vs
from vsutil import Dither, depth, get_depth

from ..better_vsutil import get_num_planes, scale_value_full
from ..helper import inject_param
from ..kernels import BicubicFC
from ._abstract import VSFilter

core = vs.core

_Deinterlacer = TypeVar('_Deinterlacer', bound='Deinterlacer')


class Deinterlacer(VSFilter, ABC):
    def __call__(self, clip: vs.VideoNode, field: int, **kwargs: Any) -> vs.VideoNode:
        return super().__vscall__(clip, field, **kwargs)


class _EdgeDirectedInterpolation(Deinterlacer, ABC):
    ...


class _AcceptExternalDeintClip(Deinterlacer, ABC):
    def __add__(self: _Deinterlacer, other: Deinterlacer) -> _Deinterlacer:
        return self.__class__(external_deint_clip=other)


class _EEDIX(_EdgeDirectedInterpolation, ABC):
    @inject_param(name='sclip')
    def __call__(self, clip: vs.VideoNode, field: int, **kwargs: Any) -> vs.VideoNode:
        return super().__call__(clip, field, **kwargs)


class NNEDI3(_EdgeDirectedInterpolation):
    """Neural Network Edge Directed Interpolation 3rd gen"""
    func = lambda: core.nnedi3.nnedi3


class NNEDI3CL(_EdgeDirectedInterpolation):
    func = lambda: core.nnedi3cl.NNEDI3CL


class ZNEDI3(_EdgeDirectedInterpolation):
    func = lambda: core.znedi3.nnedi3


class EEDI2(_EdgeDirectedInterpolation):
    func = lambda: core.eedi2.EEDI2


class EEDI3(_EEDIX):
    func = lambda: core.eedi3.eedi3


class EEDI3m(_EEDIX):
    func = lambda: core.eedi3m.EEDI3


class EEDI3mCL(_EEDIX):
    func = lambda: core.eedi3m.EEDI3CL


class SangNom2(Deinterlacer):
    func = lambda: core.sangnom.SangNom

    def __call__(self, clip: vs.VideoNode, field: int, **kwargs: Any) -> vs.VideoNode:
        order = [2, 1, 0, 0][field]
        # If field is 2 or 3 then we have to double the rate
        if not order:
            # SeparateFields and DoubleWeave must be called
            # and we determine if top field first or bottom field first
            # if field = 2 then it's TFF. If field = 3 then it's BFF
            clip = core.std.SeparateFields(clip, field % 2).std.DoubleWeave(field % 2)
        return super().__call__(clip, order, **self.params | kwargs)


class BWDiF(_AcceptExternalDeintClip):
    func = lambda: core.bwdif.Bwdif

    @inject_param(name='deint')
    def __call__(self, clip: vs.VideoNode, field: int, **kwargs: Any) -> vs.VideoNode:
        return super().__call__(clip, field, **kwargs)


class Bob(Deinterlacer):
    b: float
    c: float

    def __init__(self, b: float = 0, c: float = 1/2) -> None:
        self.b = b
        self.c = c
        super().__init__()

    def __call__(self, clip: vs.VideoNode, field: int, **kwargs: Any) -> vs.VideoNode:
        try:
            tff = [False, True][field % 2]
        except KeyError as key_err:
            raise ValueError(f'{self.__class__.__name__}: only supports double rate -> field 2 or 3') from key_err

        bits = get_depth(clip)
        fields = clip.std.SeparateFields(tff)
        clip = BicubicFC(self.b, self.c).scale(fields, None, None, scalev=2, interlaced=1, interlacedd=0)
        return depth(clip, bits, dither_type=Dither.NONE)



class NoiseDeint(VSFilter, ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def __call__(self, clip: vs.VideoNode, tff: bool = True, **kwargs: Any) -> vs.VideoNode:
        ...


class NoiseDWeave(NoiseDeint):
    def __call__(self, clip: vs.VideoNode, tff: bool = True, **kwargs: Any) -> vs.VideoNode:
        return clip.std.SeparateFields(tff).std.DoubleWeave(tff)


class NoiseBob(NoiseDeint):
    b: float
    c: float

    def __init__(self, b: float = 0, c: float = 1/2) -> None:
        self.b = b
        self.c = c
        super().__init__()

    def __call__(self, clip: vs.VideoNode, tff: bool = True, **kwargs: Any) -> vs.VideoNode:
        return Bob(self.b, self.c)(clip, tff)


class NoiseGenerate(NoiseDeint):
    def __call__(self, clip: vs.VideoNode, tff: bool = True, **kwargs: Any) -> vs.VideoNode:
        """
        Given noise extracted from an interlaced source (i.e. the noise is interlaced),
        generate "progressive" noise with a new "field" of noise injected.
        The new noise is centered on a weighted local average and uses the difference
        between local min & max as an estimate of local variance
        """
        try:
            interleaved_clip = cast(vs.VideoNode, kwargs.pop('interleaved_clip'))
            chroma = cast(bool, kwargs.pop('chroma'))
        except KeyError as key_error:
            raise ValueError from key_error

        planes = [0, 1, 2] if chroma else [0]

        noise = clip.std.SeparateFields(tff)
        noisemax = noise.std.Maximum(planes).std.Maximum(planes, coordinates=[0, 0, 0, 1, 1, 0, 0, 0])
        noisemin = noise.std.Minimum(planes).std.Minimum(planes, coordinates=[0, 0, 0, 1, 1, 0, 0, 0])

        neutral = 1 << (get_depth(clip) - 1)
        randomnoise = interleaved_clip.std.SeparateFields(tff).std.BlankClip(
            color=[neutral] * get_num_planes(clip)
        ).grain.Add(1800, 1800)

        diffnoise = core.std.MakeDiff(noisemax, noisemin, planes)

        def _scale(x: int) -> float:
            return scale_value_full(x, 8, get_depth(clip))
        varrandom = core.std.Expr([diffnoise, randomnoise], f'x {neutral} - y * {_scale(256)} / {neutral} +')
        newnoise = core.std.MergeDiff(noisemin, varrandom, planes)

        return core.std.Interleave([noise, newnoise]).std.DoubleWeave(tff)[::2]
