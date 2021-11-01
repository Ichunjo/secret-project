from __future__ import annotations

from vapoursynth import FLOAT, SampleType, VideoNode
from vsutil import (Range, disallow_variable_format, get_depth,  # noqa F401
                    get_y, scale_value)


@disallow_variable_format
def get_neutral(clip: VideoNode, /, *, chroma_plane: bool = False) -> float | int:
    assert clip.format
    if clip.format.sample_type == FLOAT:
        if chroma_plane:
            return 0.0
        return 0.5
    return 1 << (get_depth(clip) - 1)


def scale_value_full(value: float | int, input_depth: int, output_depth: int) -> float | int:
    return scale_value(value, input_depth, output_depth, Range.FULL, Range.FULL)


@disallow_variable_format
def get_num_planes(clip: VideoNode, /) -> int:
    assert clip.format
    return clip.format.num_planes


@disallow_variable_format
def get_sample_type(clip: VideoNode, /) -> SampleType:
    assert clip.format
    return clip.format.sample_type


@disallow_variable_format
def get_peak(clip: VideoNode, /) -> int:
    return 1 if get_sample_type(clip) == FLOAT else (1 << get_depth(clip)) - 1


@disallow_variable_format
def is_444(clip: VideoNode, /) -> bool:
    assert clip.format
    if all([clip.format.subsampling_w == 0, clip.format.subsampling_h == 0]):
        return True
    return False
