from __future__ import annotations

from vsutil import Range, get_y, scale_value, get_depth, disallow_variable_format  # noqa F401
from vapoursynth import VideoNode, FLOAT


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
