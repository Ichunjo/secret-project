# flake8: noqa
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
from ._preset import (
    Settings, Preset
)