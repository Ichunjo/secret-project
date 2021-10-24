
__all__ = [
    'Deinterlacer',
    'NNEDI3', 'NNEDI3CL', 'ZNEDI3', 'ZNEDI3',
    'EEDI2',
    'EEDI3', 'EEDI3m', 'EEDI3mCL',
    'SangNom2',
    'BWDiF',
    'Bob',
    'dict2class', 'class2dict'
]

from abc import ABC
from typing import Any, Dict, Type, TypeVar

import vapoursynth as vs
from vsutil import Dither, depth, get_depth

from ..helper import inject_param
from ..kernels import BicubicFC
from ..settings import VSCallableD
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


def dict2class(dico: VSCallableD) -> Deinterlacer:
    deints: Dict[str, Type[Deinterlacer]] = dict(
        nnedi3=NNEDI3, nnedi3cl=NNEDI3CL, znedi3=ZNEDI3,
        eedi2=EEDI2, eedi3=EEDI3, eedi3m=EEDI3m, eedi3mcl=EEDI3mCL,
        sangnom2=SangNom2, bwdif=BWDiF, bob=Bob
    )
    if (kwargs := dico['args']) is None:
        kwargs = {}

    try:
        clss = deints[dico['name']]
    except KeyError as key_err:
        raise ValueError from key_err

    return clss(**kwargs)


def class2dict(deint: Deinterlacer) -> VSCallableD:
    return VSCallableD(name=deint.__class__.__name__, args=deint.params)
