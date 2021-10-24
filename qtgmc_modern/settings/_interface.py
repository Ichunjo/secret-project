
__all__ = [
    'CoreParam', 'CoreSettings',
    'VSCallableD',
    'InterpolationSettings',
    'MotionAnalysisSettings',
    'SharpnessSettings',
    'SourceMatchSettings',
    'NoiseSettings',

    'Settings',

    'SearchPre', 'SubPel', 'SubPelInter', 'Search', 'PLevel',
    'InputType'
]

from enum import IntEnum
from typing import TYPE_CHECKING, Any, Dict, Optional, TypedDict

from ._abstract import LoggedSettings

if TYPE_CHECKING:
    # Features / Settings dicts
    class VSCallableD(TypedDict):
        name: str
        args: Optional[Dict[str, Any]]


    class CoreParam(TypedDict):
        tr: int
        """Temporal binomial/linear smoothing radius used"""
        rep: int
        """Repair unwanted blur after temporal smooth"""


    class CoreSettings(TypedDict):
        motion_search: CoreParam
        """Motion search clip"""
        initial_output: CoreParam
        """Interpolated clip for inital output"""
        final_output: CoreParam

    class InterpolationSettings(TypedDict):
        deint: VSCallableD
        deint_chroma: Optional[VSCallableD]
        ref: Optional[bool]


    class MotionAnalysisSettings(TypedDict):
        searchpre: int
        """Pre-filtering for motion search clip | SrchClipPP"""
        subpel: int
        subpel_inter: int
        blocksize: int
        overlap: int
        search: int
        search_param: int
        pelsearch: int
        chroma_motion: bool
        truemotion: bool
        lambda_: Optional[int]
        lsad: Optional[int]
        pnew: Optional[int]
        plevel: Optional[int]
        globalmotion: bool
        dct: int
        thsad_initial_output: int
        thsad_final_output: int
        thscd1: int
        thscd2: int


    class SharpnessSettings(TypedDict):
        strength: float
        mode: int
        lmode: int
        lrad: int
        ovs: int
        vthin: float
        bb: int


    class SourceMatchSettings(TypedDict):
        match: int
        """SourceMatch"""
        lossless: int
        """Lossless"""

        basic_deint: VSCallableD
        """MatchEdi"""

        refined_deint: VSCallableD
        """MatchEdi2"""
        refined_tr: int
        """MatchTR2"""
        enhance: float
        """MatchEnhance"""


    class NoiseSettings(TypedDict):
        mode: int
        denoiser: VSCallableD
        use_mc: bool
        tr: int
        strength: float
        chroma: bool
        restore_before_final: float
        restore_after_final: float
        deint: VSCallableD
        stabilise: bool


    class Settings(TypedDict):
        core: CoreSettings
        motion_analysis: MotionAnalysisSettings
        interpolation: InterpolationSettings
        sharpness: SharpnessSettings
        source_match: SourceMatchSettings

        identify_noise: Optional[NoiseSettings]
        # noise
        # progressive
        # shutter speed motion blur framerate
else:
    class VSCallableD(LoggedSettings): ...  # noqa E701
    class CoreParam(LoggedSettings): ...  # noqa E701
    class CoreSettings(LoggedSettings): ...  # noqa E701
    class InterpolationSettings(LoggedSettings): ...  # noqa E701
    class MotionAnalysisSettings(LoggedSettings): ...  # noqa E701
    class SharpnessSettings(LoggedSettings): ...  # noqa E701
    class SourceMatchSettings(LoggedSettings): ...  # noqa E701
    class NoiseSettings(LoggedSettings): ...  # noqa E701
    class Settings(LoggedSettings): ...  # noqa E701

# class PresetSettings(TypedDict):
#     PLACEBO: Settings
#     VERY_SLOW: Settings
#     SLOWER: Settings
#     SLOW: Settings
#     MEDIUM: Settings
#     FAST: Settings
#     FASTER: Settings
#     VERY_FAST: Settings
#     SUPER_FAST: Settings
#     ULTRA_FAST: Settings
#     DRAFT: Settings


# Enums
# Motion Anal
class SearchPre(IntEnum):
    """Pre-filtering for motion search clip"""
    NONE = 0
    SIMPLE_BLUR = 1
    GAUSSIAN = 2
    GAUSSIAN_EDGE_SOFTEN = 3


class SubPel(IntEnum):
    """Sub-pixel accuracy for motion analysis"""
    ONE = 1
    HALF = 2
    QUARTER = 4


class SubPelInter(IntEnum):
    """Interpolation used for sub-pixel motion analysis"""
    BILINEAR = 0
    BICUBIC = 1
    WEINER = 2


class Search(IntEnum):
    ONETIME = 0
    NSTEP = 1
    LOGARITHMIC = 2
    EXHAUSTIVE = 3
    HEXAGON = 4
    UNEVEN_MULTI_HEXAGON = 5
    HORIZONTAL_EXHAUSTIVE = 6
    VERTICAL_EXHAUSTIVE = 7


class PLevel(IntEnum):
    """Penality factor lambda level scaling mode"""
    NO_SCALING = 0
    LINEAR = 1
    QUADRATIC = 2
    """Quadratic dependence from hierarchical level size"""


# InputType
class InputType(IntEnum):
    INTERLACED_ONLY = 0
    PROGRESSIVE_GENERIC = 1
    PROGRESSIVE_VERYBAD = 2
    PROGRESSIVE_VERYBAD_INV_FIELD = 3
