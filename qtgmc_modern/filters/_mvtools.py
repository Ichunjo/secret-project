"""
MVTools interface
"""

__all__ = [
    'mv_analyse',
    'mv_super',
    'mv_compensate',
    'mv_mask',
    'mv_degrain1',
    'mv_recalculate',
    'mv_flowblur'
]

from typing import Any, Callable
import vapoursynth as vs

from ..better_vsutil import get_sample_type


def _pick_function(clip: vs.VideoNode,
                   func_int: Callable[..., vs.VideoNode],
                   func_float: Callable[..., vs.VideoNode]) -> Callable[..., vs.VideoNode]:
    return func_float if get_sample_type(clip) == vs.FLOAT else func_int


def mv_analyse(clip: vs.VideoNode, **kwargs: Any) -> vs.VideoNode:
    return _pick_function(clip, vs.core.mv.Analyse, vs.core.mvsf.Analyse)(clip, **kwargs)


def mv_super(clip: vs.VideoNode, **kwargs: Any) -> vs.VideoNode:
    return _pick_function(clip, vs.core.mv.Super, vs.core.mvsf.Super)(clip, **kwargs)


def mv_compensate(clip: vs.VideoNode, **kwargs: Any) -> vs.VideoNode:
    return _pick_function(clip, vs.core.mv.Compensate, vs.core.mvsf.Compensate)(clip, **kwargs)


def mv_mask(clip: vs.VideoNode, **kwargs: Any) -> vs.VideoNode:
    return _pick_function(clip, vs.core.mv.Mask, vs.core.mvsf.Mask)(clip, **kwargs)


def mv_degrain1(clip: vs.VideoNode, **kwargs: Any) -> vs.VideoNode:
    return _pick_function(clip, vs.core.mv.Degrain1, vs.core.mvsf.Degrain1)(clip, **kwargs)


def mv_recalculate(clip: vs.VideoNode, **kwargs: Any) -> vs.VideoNode:
    return _pick_function(clip, vs.core.mv.Recalculate, vs.core.mvsf.Recalculate)(clip, **kwargs)


def mv_flowblur(clip: vs.VideoNode, **kwargs: Any) -> vs.VideoNode:
    return _pick_function(clip, vs.core.mv.FlowBlur, vs.core.mvsf.FlowBlur)(clip, **kwargs)
