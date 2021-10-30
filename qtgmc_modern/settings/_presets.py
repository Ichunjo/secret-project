from enum import Enum
from typing import Any, Dict, NamedTuple

from ._interface import VSCallableD


class NNEDI3Preset(Dict[str, Any], Enum):
    PLACEBO =    dict(nsize=1, nns=2)  # noqa: E222
    VERYSLOW =   dict(nsize=1, nns=2)  # noqa: E222
    SLOWER =     dict(nsize=1, nns=1)  # noqa: E222
    SLOW =       dict(nsize=1, nns=1)  # noqa: E222
    MEDIUM =     dict(nsize=5, nns=1)  # noqa: E222
    FAST =       dict(nsize=5, nns=0)  # noqa: E222
    FASTER =     dict(nsize=4, nns=0)  # noqa: E222
    VERYFAST =   dict(nsize=4, nns=0)  # noqa: E222
    SUPERFAST =  dict(nsize=4, nns=0)  # noqa: E222
    ULTRAFAST =  dict(nsize=4, nns=0)  # noqa: E222
    DRAFT =      dict(nsize=4, nns=0)  # noqa: E222


class EEDI3Preset(Dict[str, Any], Enum):
    PLACEBO =    dict(mdis=12)  # noqa: E222
    VERYSLOW =   dict(mdis=10)  # noqa: E222
    SLOWER =     dict(mdis=18)  # noqa: E222
    SLOW =       dict(mdis=7)  # noqa: E222
    MEDIUM =     dict(mdis=7)  # noqa: E222
    FAST =       dict(mdis=6)  # noqa: E222
    FASTER =     dict(mdis=6)  # noqa: E222
    VERYFAST =   dict(mdis=2)  # noqa: E222
    SUPERFAST =  dict(mdis=4)  # noqa: E222
    ULTRAFAST =  dict(mdis=4)  # noqa: E222
    DRAFT =      dict(mdis=4)  # noqa: E222


class NoisePreset(Dict[str, Any], Enum):
    SLOWER = dict(
        denoiser=VSCallableD(name='dfttest', args=None),
        use_mc=True,
        tr=2,
        deint=VSCallableD(name='generate', args=None),
        stabilise=True
    )
    SLOW = dict(
        denoiser=VSCallableD(name='dfttest', args=None),
        use_mc=True,
        tr=1,
        deint=VSCallableD(name='bob', args=None),
        stabilise=True
    )
    MEDIUM = dict(
        denoiser=VSCallableD(name='dfttest', args=None),
        use_mc=False,
        tr=1,
        deint=VSCallableD(name='DoubleWeave', args=None),
        stabilise=True
    )
    FAST = dict(
        denoiser=VSCallableD(name='fft3d', args=None),
        use_mc=False,
        tr=1,
        deint=VSCallableD(name='DoubleWeave', args=None),
        stabilise=False
    )
    FASTER = dict(
        denoiser=VSCallableD(name='fft3d', args=None),
        use_mc=False,
        tr=0,
        deint=VSCallableD(name='DoubleWeave', args=None),
        stabilise=False
    )


class _PresetTuple(NamedTuple):
    name: str
    i: int


class Preset(_PresetTuple, Enum):
    # PLACEBO = 'placebo'
    # VERYSLOW = 'veryslow'
    # SLOWER = 'slower'
    # SLOW = 'slow'
    # MEDIUM = 'medium'
    # FAST = 'fast'
    # FASTER = 'faster'
    # VERYFAST = 'veryfast'
    # SUPERFAST = 'superfast'
    # ULTRAFAST = 'ultrafast'
    # DRAFT = 'draft'
    PLACEBO =   _PresetTuple('placebo', 0)  # noqa: E222
    VERYSLOW =  _PresetTuple('veryslow', 1)  # noqa: E222
    SLOWER =    _PresetTuple('slower', 2)  # noqa: E222
    SLOW =      _PresetTuple('slow', 3)  # noqa: E222
    MEDIUM =    _PresetTuple('medium', 4)  # noqa: E222
    FAST =      _PresetTuple('fast', 5)  # noqa: E222
    FASTER =    _PresetTuple('faster', 6)  # noqa: E222
    VERYFAST =  _PresetTuple('veryfast', 7)  # noqa: E222
    SUPERFAST = _PresetTuple('superfast', 8)  # noqa: E222
    ULTRAFAST = _PresetTuple('ultrafast', 9)  # noqa: E222
    DRAFT =     _PresetTuple('draft', 10)  # noqa: E222
