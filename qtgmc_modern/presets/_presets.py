from enum import Enum
from typing import Any, Dict, NamedTuple


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


class _P(NamedTuple):
    name: str
    i: int


class Preset(_P, Enum):
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
    PLACEBO =   _P('placebo', 0)  # noqa: E222
    VERYSLOW =  _P('veryslow', 1)  # noqa: E222
    SLOWER =    _P('slower', 2)  # noqa: E222
    SLOW =      _P('slow', 3)  # noqa: E222
    MEDIUM =    _P('medium', 4)  # noqa: E222
    FAST =      _P('fast', 5)  # noqa: E222
    FASTER =    _P('faster', 6)  # noqa: E222
    VERYFAST =  _P('veryfast', 7)  # noqa: E222
    SUPERFAST = _P('superfast', 8)  # noqa: E222
    ULTRAFAST = _P('ultrafast', 9)  # noqa: E222
    DRAFT =     _P('draft', 10)  # noqa: E222
