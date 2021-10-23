from enum import Enum, auto
from typing import NamedTuple

from ._core import (
    # Makers
    CoreSettings, CoreParam,
    # Default CoreSettings
    core_placebo,
    core_veryslow,
    core_slower,
    core_slow,
    core_medium,
    core_fast,
    core_faster,
    core_veryfast,
    core_superfast,
    core_ultrafast,
    core_draft
)
from ._interpolation import (
    # Maker
    InterpolationSettings,
    # Default InterpolationSettings
    interpolation_placebo,
    interpolation_veryslow,
    interpolation_slower,
    interpolation_slow,
    interpolation_medium,
    interpolation_fast,
    interpolation_faster,
    interpolation_veryfast,
    interpolation_superfast,
    interpolation_ultrafast,
    interpolation_draft
)
from ._motion_anal import (
    # Makers
    MotionAnalysisSettings,
    SearchPre, SubPel, SubPelInter, Search, PLevel,
    # Default MotionAnalysisSettings
    motion_analysis_placebo,
    motion_analysis_veryslow,
    motion_analysis_slower,
    motion_analysis_slow,
    motion_analysis_medium,
    motion_analysis_fast,
    motion_analysis_faster,
    motion_analysis_veryfast,
    motion_analysis_superfast,
    motion_analysis_ultrafast,
    motion_analysis_draft
)


class Settings(NamedTuple):
    core: CoreSettings
    motion_analysis: MotionAnalysisSettings
    interpolation: InterpolationSettings
    # sharpness
    # souce_match
    # noise
    # progressive
    # shutter speed motion blur framerate


class Preset(Settings, Enum):
    PLACEBO = Settings(
        core_placebo,
        motion_analysis_placebo,
        interpolation_placebo
    )
    VERY_SLOW = Settings(
        core_veryslow,
        motion_analysis_veryslow,
        interpolation_veryslow
    )
    SLOWER = Settings(
        core_slower,
        motion_analysis_slower,
        interpolation_slower
    )
    SLOW = Settings(
        core_slow,
        motion_analysis_slow,
        interpolation_slow
    )
    MEDIUM = Settings(
        core_medium,
        motion_analysis_medium,
        interpolation_medium
    )
    FAST = Settings(
        core_fast,
        motion_analysis_fast,
        interpolation_fast
    )
    FASTER = Settings(
        core_faster,
        motion_analysis_faster,
        interpolation_faster
    )
    VERY_FAST = Settings(
        core_veryfast,
        motion_analysis_veryfast,
        interpolation_veryfast
    )
    SUPER_FAST = Settings(
        core_superfast,
        motion_analysis_superfast,
        interpolation_superfast
    )
    ULTRA_FAST = Settings(
        core_ultrafast,
        motion_analysis_ultrafast,
        interpolation_ultrafast
    )
    DRAFT = Settings(
        core_draft,
        motion_analysis_draft,
        interpolation_draft
    )
